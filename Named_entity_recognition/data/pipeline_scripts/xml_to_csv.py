from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os
import glob
from tqdm import tqdm
from deep_translator import GoogleTranslator

from py4j.java_gateway import JavaGateway
import time
from time import sleep
import subprocess
import atexit
import ujson as json

import spacy
import sys
import signal
import traceback
import multiprocessing
from spacy.matcher import PhraseMatcher
from spacy.lang.en.stop_words import STOP_WORDS
from tei_validator import validate_tei_file

java_process = subprocess.Popen(
    ['java', '-jar', '-Dfile.encoding=UTF-8', 'corese-library-python-4.4.1.jar'])
sleep(6)
gateway = JavaGateway()

_gateway_stopped = False


def exit_handler():
    global _gateway_stopped
    if _gateway_stopped:
        return
    _gateway_stopped = True
    try:
        gateway.shutdown()
    except Exception:
        pass
    print('\n' * 2)
    print('Gateway Server Stop!')

atexit.register(exit_handler)

Graph = gateway.jvm.fr.inria.corese.core.Graph
Load = gateway.jvm.fr.inria.corese.core.load.Load
Transformer = gateway.jvm.fr.inria.corese.core.transform.Transformer
QueryProcess = gateway.jvm.fr.inria.corese.core.query.QueryProcess
RDF = gateway.jvm.fr.inria.corese.core.logic.RDF
RESULTFORMAT = gateway.jvm.fr.inria.corese.core.print.ResultFormat
coreseFormat = gateway.jvm.fr.inria.corese.sparql.api.ResultFormatDef

MAX_TRIES = 50

def sparqlQuery(graph, query):
    exec = QueryProcess.create(graph)
    return exec.query(query)

def convert_sparql_to_json(mapping_object):
    sparql_formater = RESULTFORMAT.create(mapping_object)
    sparql_formater.setSelectFormat(coreseFormat.JSON_FORMAT)

    json_convert = json.loads(sparql_formater.toString())
    return json_convert

def load(graph ,path):
    ld = Load.create(graph)
    ld.parse(path)

    return graph

API_ENDPOINT_URL = "http://nerd.huma-num.fr/nerd/service"
DBPEDIA_LOCAL = 'http://localhost:2222/rest'

nlp_model = spacy.load("en_core_web_lg")

SUPPORTED_DIV = ["poem", "book", "chapter", "section", "edition"]
ANNOTATION_AUTO = True

class _TranslateTimeout(Exception):
    pass


def _on_translate_alarm(signum, frame):
    raise _TranslateTimeout()


def _translate_with_timeout(text, lang_target, seconds=45):
    """GoogleTranslator().translate() borne dans le temps. deep_translator
    n'expose pas de timeout et s'appuie sur requests sans delai : une seule
    requete qui reste silencieusement bloquee (cote Google) fige tout le
    pipeline indefiniment (cas rencontre plusieurs fois - zoo87, zoo7/1g).
    SIGALRM interrompt l'appel au bout de `seconds` ; si le signal n'est pas
    disponible (thread secondaire), on retombe sur l'appel nu."""
    try:
        previous = signal.signal(signal.SIGALRM, _on_translate_alarm)
    except (ValueError, AttributeError):
        return GoogleTranslator(source='auto', target=lang_target).translate(text)
    signal.alarm(seconds)
    try:
        return GoogleTranslator(source='auto', target=lang_target).translate(text)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


# Reponses que deep_translator renvoie SANS lever d'exception quand Google
# sert une page d'erreur HTTP 200 (typiquement sous limitation de debit apres
# quelques centaines d'appels rapides) : la chaine passe alors pour une
# "traduction" et son texte ("Server Error (500)"...) est annote a la place du
# vrai contenu - meme jeu d'annotations colle sur des centaines de paragraphes
# (bug decouvert sur zoo7/5g, 560/889 paragraphes, et zoo7/6g). A traiter
# comme un echec (backoff long : la limitation Google se leve en dizaines de
# secondes, pas en 5).
_TRANSLATE_ERROR_MARKERS = (
    "server error", "bad gateway", "service unavailable", "too many requests",
    "error 500", "error 502", "error 503", "http error", "<html", "gateway timeout",
)


def _looks_like_translate_error(result, source):
    if result is None:
        return True
    stripped = result.strip()
    if stripped == "":
        return True
    low = stripped.lower()
    if any(marker in low for marker in _TRANSLATE_ERROR_MARKERS):
        return True
    # Reponse anormalement courte pour une entree substantielle (une page
    # d'erreur laconique la ou on attend une vraie traduction).
    if len(source) > 60 and len(stripped) < max(12, 0.12 * len(source)):
        return True
    return False


def split_and_translate(text, lang_target, max_chunk_length=4500):
    # 4500 plutot que 1000 (valeur d'origine) : l'endpoint gratuit de Google
    # Translate tolere generalement jusqu'a ~5000 caracteres par requete (non
    # documente officiellement, mais constate empiriquement). deep_translator
    # n'offre aucun vrai regroupement de requetes (translate_batch() n'est
    # qu'une boucle interne appelant translate() un par un, verifie dans son
    # code source) - le seul levier reel pour reduire le nombre de requetes
    # est donc de MOINS decouper : un paragraphe de 4000 caracteres faisait
    # 4 requetes separees avec l'ancienne limite de 1000, contre 1 seule ici.
    # Moins de requetes = moins de risque de declencher la limitation de
    # debit externe qui domine le temps de traitement (voir sections 22-23
    # de la doc pour l'historique de ce probleme).
    chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
    translated_chunks = []

    for chunk in chunks:
        tries = 0
        success = False
        while not success:
            try:
                translated_chunk = _translate_with_timeout(chunk, lang_target)
                if _looks_like_translate_error(translated_chunk, chunk):
                    raise RuntimeError("reponse Google Translate invalide (page d'erreur)")
                translated_chunks.append(translated_chunk)
                success = True

            except Exception as e:
                tries += 1
                if tries >= 8:
                    # Google ne repond plus correctement pour ce segment : on le
                    # laisse en langue source (le NER y trouvera moins d'entites,
                    # mais pas de fausses annotations "Server Error") plutot que
                    # de bloquer tout le corpus.
                    print(f" Google Translate injoignable apres {tries} tentatives ; segment laisse en langue source.")
                    translated_chunks.append(chunk)
                    success = True
                    continue
                wait = min(15 * tries, 120)
                print(f" Echec/blocage Google Translate (tentative {tries}: {e}). Reessai dans {wait}s...")
                time.sleep(wait)

        # Pacing leger entre segments : evite de declencher la limitation de
        # debit de Google sur les oeuvres a plusieurs centaines de paragraphes
        # entierement traduites par machine (zoo7/5g, zoo81...).
        time.sleep(0.4)

    translated_text = ' '.join(translated_chunks)
    return translated_text


def is_stop_word(word):
    if word.text.lower() not in STOP_WORDS:
        return False
    elif len(word) == 1:
        token = word[0]
        return token.pos_ != "PROPN"
    else:
        return all(token.pos_ != "PROPN"
                   for token in word)


def get_NER_from_dbpedia(element,lg="en"):
    if not element or element.strip() == "":
        return []
    if "entityfishing" in list(map(lambda x: x[0], nlp_model.pipeline)):
        nlp_model.remove_pipe("entityfishing")
    if not "dbpedia_spotlight" in list(map(lambda x: x[0], nlp_model.pipeline)):
        nlp_model.add_pipe('dbpedia_spotlight',
                           config={'dbpedia_rest_endpoint': DBPEDIA_LOCAL, 'confidence': 0.3})
    return process_nlp(element, nlp_model)


def get_NER_from_wikidata(element, lg="en"):
    if not element or element.strip() == "":
        return []
    if "dbpedia_spotlight" in list(map(lambda x: x[0], nlp_model.pipeline)):
        nlp_model.remove_pipe("dbpedia_spotlight")
    if not "entityfishing" in list(map(lambda x: x[0], nlp_model.pipeline)):
        nlp_model.add_pipe("entityfishing", config={"language": "en", "api_ef_base": API_ENDPOINT_URL})
    return process_nlp(element,nlp_model)


def process_nlp(element,nlp_model):
    error = None

    for tries in range(MAX_TRIES):
        try:
            en_text = nlp_model(element)
            return en_text.ents

        except Exception as e:
            attente = min(5 * ++tries, 60)
            print(f"Echec du traitement nlp (Tentative {tries}). Reessai dans {attente}s...")
            if tries==MAX_TRIES:
                error = e
            time.sleep(attente)

    print(error)
    print(f"Echec lors du traitement avec le nlp sur {element}. Ignore.")
    print(FILE)
    return []


def find_thesaurus_entities(translated_paragraph, annotations, paragraph):
    if not translated_paragraph or translated_paragraph.strip() == "":
        return
    pipes_to_disable = ["dbpedia_spotlight", "entityfishing", "ner"]
    active_disables = [pipe for pipe in pipes_to_disable if pipe in nlp_model.pipe_names]
    with nlp_model.select_pipes(disable=active_disables):
        doc = nlp_model(translated_paragraph)

    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        if not is_stop_word(span):
            annotations.append([
                paragraph,
                thesaurus_dict[nlp_model.vocab.strings[match_id]],
                span.text,
                1,
                "zoomathia_match"
            ])


def extract_dbpedia(entities, annotations, paragraph):
    for ent in entities:
        if ent.kb_id_ == None or ent.kb_id_ == '':
            continue
        if is_stop_word(ent):
            continue
        if ent.kb_id_ is not None:
            annotations.append([paragraph,
                            ent.kb_id_,
                            ent.text,
                            ent._.dbpedia_raw_result['@similarityScore'],
                            "DBpedia"])


def extract_wikidata(entities, annotations, paragraph):
    for ent in entities:
        if ent._.url_wikidata is None or ent._.url_wikidata == '':
            continue
        if is_stop_word(ent):
            continue
        if ent._.nerd_score is not None and ent._.nerd_score >= 0.3:

            annotations.append([paragraph,
                                ent._.url_wikidata,
                                ent.text,
                                ent._.nerd_score,
                                "wikidata"])


AUTHOR_CONCORDANCE_PATHS = [
    "repertoire_zoo/repertoire_codes_zoo.csv",
]


def load_canonical_authors(paths=AUTHOR_CONCORDANCE_PATHS):
    """Table zooN -> nom canonique de l'auteur.
    Chaque fichier XML ecrit le nom d'auteur a sa maniere (ex: 'Aristotle' vs
    'ARISTOTELES'), ce qui fragmente le meme auteur en plusieurs valeurs dans
    le graphe. repertoire_zoo/repertoire_codes_zoo.csv associe un seul nom
    canonique par dossier zooN : on l'utilise comme source de verite plutot
    que le texte brut du XML. Le second fichier ne sert qu'a completer les
    quelques dossiers absents du premier (ex: zoo1)."""
    mapping = {}
    # Ordre: les fichiers suivants ne comblent que les trous, sans ecraser
    # une entree deja trouvee dans un fichier precedent (priorite au premier).
    for path in paths:
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            code = str(row["code_zoo"]).strip()
            if "/" not in code:
                continue
            folder = code.split("/", 1)[0]
            mapping.setdefault(folder, str(row["nom_canonique"]).strip())
    return mapping


CANONICAL_AUTHORS = load_canonical_authors()


def extract_sourcedesc_data(source):
    """
        Extract metadata from XML-TEI header
        *Those information cannot be found in the body*
    """

    date = strip_text(source.sourceDesc.date.text) if source.sourceDesc and source.sourceDesc.date \
        else strip_text(source.titleStmt.date.text) if source.titleStmt and source.titleStmt.date else strip_text(
        source.publicationStmt.date.text) if source.publicationStmt and source.publicationStmt.date else "date not found"
    editor = strip_text(source.titleStmt.editor.text) if source.titleStmt and source.titleStmt.editor else "Unknown editor"

    author_tag = (source.titleStmt.author if source.titleStmt and source.titleStmt.author
                  else source.sourceDesc.author if source.sourceDesc and source.sourceDesc.author else None)
    if author_tag and author_tag.persName:
        author = strip_text(author_tag.persName.text)
    elif author_tag:
        author = strip_text(author_tag.text)
    else:
        author = 'Author not found'

    # Choix du titre: prefere un <title type="alt"> deja dans la bonne langue
    # (evite de traduire via Google Translate un titre deja correct) avant de
    # retomber sur le <head> direct de <text>, puis sur le titre principal traduit.
    title_tag = None
    if source.titleStmt:
        primary_title_tag = source.titleStmt.find("title")
        file_lang = primary_title_tag.get("xml:lang") if primary_title_tag else None
        for lang in filter(None, [file_lang, "en"]):
            title_tag = source.titleStmt.find("title", attrs={"type": "alt", "xml:lang": lang})
            if title_tag:
                break

    if title_tag:
        oeuvre_title = strip_text(title_tag.text)
    else:
        text_tag = source.find("text")
        direct_head = text_tag.find("head", recursive=False) if text_tag else None
        if direct_head and strip_text(direct_head.text):
            oeuvre_title = strip_text(direct_head.text)
        elif source.titleStmt and source.titleStmt.title:
            # Titre classique (latin/grec) garde tel quel: pas de traduction automatique,
            # qui peut faire coincider par erreur des oeuvres differentes (bug constate).
            oeuvre_title = strip_text(source.titleStmt.title.text)
        else:
            oeuvre_title = "title not found"

    oeuvre_id = oeuvre_title.replace(" ", "_").lower() if oeuvre_title != "title not found" else "id_not_found"

    return oeuvre_id, oeuvre_title, author, date, editor


def does_it_have_children_div(node):
    """
        Check if the given node has "div-like" children
        div-like => div1, div2... tags that start with 'div'
    """
    return node.find_all(re.compile('^div'))


def strip_text(txt):
    txt = txt.strip().replace("\r", "").replace("\n", "").replace("\t", "").replace("\"", "").replace("- ", "")
    return re.sub(r"\s+", " ", txt)


def clean_uri(txt):
    if not txt or txt.strip() == "":
        return ""
    try:
        translated_txt = _translate_with_timeout(txt, "en")
    except Exception as e:
        print(f"[WARNING] Erreur de traduction du titre/auteur pour: '{txt}' : {e}")
        translated_txt = txt
    txt = translated_txt.strip().replace("\r", "").replace("\n", "").replace("\t", "").replace("\"", "").replace("- ", "")
    return re.sub(r"\s+", " ", txt)

def strip_paragraph_text(txt):
    txt = txt.strip().replace("\r", "").replace("\n", " ").replace("\t", "").replace("\"", "'").replace("- ", "")
    return re.sub(r"\s+", " ", txt)


def find_xml_files(directory):
    pattern = os.path.join(directory, '**', '*.xml')
    xml_files = glob.glob(pattern, recursive=True)
    return xml_files


def get_witness_lang(file_path):
    """Zoo naming convention: <n><lang letter>[_<n>].xml, e.g. 1e.xml, 1g_3.xml.
    Renvoie la lettre de langue (e=anglais, g=grec, l=latin, f=francais...),
    ou "" si le nom de fichier ne suit pas la convention. Fiable a 100% sur
    les 263 fichiers du corpus (verifie), contrairement a l'attribut XML
    xml:lang qui est souvent absent."""
    basename = os.path.basename(file_path)
    match = re.match(r"^\d+([a-z])(_\d+)?\.xml$", basename)
    return match.group(1) if match else ""


def is_english_file(file_path):
    """Zoo naming convention: <n><lang letter>[_<n>].xml, e.g. 1e.xml, 1e_3.xml. 'e' = anglais."""
    return get_witness_lang(file_path) == "e"


def get_witness_suffix(file_path):
    """Suffixe numerique du fichier (ex. "_2" pour "1l_2.xml"), ou "" s'il n'y
    en a pas. Deux temoins d'une meme langue peuvent partager le meme titre
    (ex. zoo20/1l_1.xml et zoo20/1l_2.xml, deux editions de Cynegetica :
    Haupt 1838 vs The Latin Library), ce qui leur donnerait sinon la meme
    URI (auteur+titre+langue) et ferait fusionner a tort leurs paragraphes
    dans le graphe. On ajoute donc ce suffixe a l'URI uniquement quand un
    autre fichier du meme dossier partage la meme lettre de langue -
    inutile (mais inoffensif) pour les cas ou les titres different deja."""
    basename = os.path.basename(file_path)
    match = re.match(r"^(\d+)([a-z])(_\d+)?\.xml$", basename)
    if not match:
        return ""
    number, lang, suffix = match.groups()
    if not suffix:
        return ""
    folder = os.path.dirname(file_path)
    siblings = [
        f for f in os.listdir(folder)
        if re.match(rf"^{re.escape(number)}{re.escape(lang)}(_\d+)?\.xml$", f)
    ]
    return suffix if len(siblings) > 1 else ""


# Oeuvres dont le temoin anglais n'est PAS bon a reutiliser malgre un pairage
# automatique trouve par le nom de fichier (voir find_english_witness_file
# ci-dessous) - typiquement une anomalie qui necessite une reprise du fichier
# lui-meme, pas seulement un ajustement de l'algorithme d'alignement. Cle =
# "zooN/numero" (ex. "zoo26/2"). Vide pour l'instant : les deux cas identifies
# a ce jour (Strabon zoo49/1, decalage de position du a des divisions
# paratextuelles non numerotees ; Lucien zoo26/2, encodage en vers errone +
# oeuvre parasite + page manquante) ont ete corriges a la source plutot que
# contournes ici. Voir DOCUMENTATION_SYSTEME_ZOO.md section 21.
ENGLISH_WITNESS_EXCLUDE = {}

_english_alignment_cache = {}
# Compteurs de diagnostic (paragraphes ou une traduction alignee a ete
# trouvee vs. non trouvee/repli sur Google Translate), par fichier non-anglais
# traite - permet de reperer apres coup une oeuvre au taux de succes anormalement
# bas (meme logique que le cas Strabon ci-dessus) sans avoir a mesurer un score
# de concordance a l'avance sur un texte qu'on n'a pas encore reellement traite.
_alignment_stats = {}


def get_witness_number(file_path):
    """Numero d'oeuvre du fichier (convention <numero><lettre>[_variante].xml,
    ex: "5g_2.xml" -> "5"), ou "" si le nom ne suit pas la convention."""
    basename = os.path.basename(file_path)
    match = re.match(r"^(\d+)[a-z](_\d+)?\.xml$", basename)
    return match.group(1) if match else ""


def find_english_witness_file(non_english_file_path):
    """Trouve automatiquement, dans le meme dossier zooN, le fichier temoin
    anglais correspondant au meme numero d'oeuvre que non_english_file_path
    (convention de nommage <numero><lettre>[_variante].xml : le temoin
    anglais de "5g.xml" est "5e.xml"). Prefere le fichier sans variante
    ("5e.xml") ; a defaut prend le premier "5e_N.xml" trouve par ordre
    alphabetique. Retourne None si aucun numero n'est detecte ou si aucun
    fichier anglais correspondant n'existe (l'oeuvre n'a alors simplement pas
    de traduction humaine a reutiliser, ce qui est le cas normal pour la
    majorite du corpus)."""
    num = get_witness_number(non_english_file_path)
    if not num:
        return None
    folder = os.path.dirname(non_english_file_path)
    exact = f"{num}e.xml"
    if os.path.exists(os.path.join(folder, exact)):
        return exact
    try:
        candidates = sorted(
            f for f in os.listdir(folder)
            if re.match(rf"^{re.escape(num)}e_\d+\.xml$", f)
        )
    except OSError:
        return None
    return candidates[0] if candidates else None


def _walk_english_paragraphs(div, path, out_map):
    """Parcourt recursivement les div type=book/chapter... d'un temoin anglais
    deja traduit par un humain, avec la meme logique positionnelle que
    extract_division_metadata, et associe a chaque chemin (ex: (1,1) pour
    livre 1 chapitre 1) le texte concatene de ses paragraphes <p>."""
    children = div.find_all(re.compile("^div"), recursive=False)

    # Enveloppe transparente (ex: <div type="translation">/"edition" autour de
    # tout le texte, zoo24/1e, zoo26/1e/2e, zoo47/1e) : seul enfant a ce niveau,
    # sans numero reel (n= absent ou non numerique) - ne compte pas comme un
    # niveau de chemin, sans quoi tout l'alignement est decale d'un cran
    # (chapitre 1 grec compare a l'enveloppe entiere plutot qu'au chapitre 1
    # anglais). Le n= numerique est le signal qui evite de confondre ceci avec
    # une vraie division unique legitime (ex: zoo85 Solinus, un seul livre
    # n="1" - celui-la doit rester compte normalement, cote grec ayant la
    # meme unique division). Teste sur le nombre d'ENFANTS de tag_div, pas
    # sur len(children) du niveau courant (un seul type="poem" a cote d'un
    # type="book" numerique n'est pas une enveloppe, juste une div en trop -
    # gere plus bas par le filtre n= non numerique). DOCUMENTATION_SYSTEME_ZOO.md
    # section 21.
    if len(children) == 1:
        only = children[0]
        only_n = only.get("n", "")
        if (not only_n or not only_n.isdigit()) and does_it_have_children_div(only):
            _walk_english_paragraphs(only, path, out_map)
            return

    position = 0
    for tag_div in children:
        # Paratexte non numerote au milieu de vraies divisions numerotees
        # (ex: Strabon zoo49/1e - un "book" n="front" avant le livre 1, un
        # "chapter" n="argument" avant le chapitre 1 de chaque livre) sans
        # equivalent cote grec, qui decale sinon la position de toutes les
        # divisions numerotees suivantes. Cote non-anglais, une division de
        # contenu reel porte toujours un n= purement numerique - on ignore
        # donc (sans consommer de position, sans y descendre) toute div dont
        # le n= ne l'est pas. Voir DOCUMENTATION_SYSTEME_ZOO.md section 21.
        div_n = tag_div.get("n", "")
        if div_n and not div_n.isdigit():
            continue
        position += 1
        current_path = path + (position,)
        if does_it_have_children_div(tag_div):
            _walk_english_paragraphs(tag_div, current_path, out_map)
        else:
            texts = []
            for p in tag_div.find_all(["p"]):
                if not p.find_parent('p') and strip_text(p.text) != "":
                    texts.append(strip_paragraph_text(p.text))
            if texts:
                out_map[current_path] = " ".join(texts)


def get_english_alignment_map(non_english_file_path):
    """Retourne (et met en cache par "zooN/numero") la correspondance chemin
    (livre, chapitre, ...) -> texte anglais deja traduit humainement, pour
    l'oeuvre donnee, si un temoin anglais correspondant est trouve (voir
    find_english_witness_file) et n'est pas explicitement exclu
    (ENGLISH_WITNESS_EXCLUDE). None si aucun temoin anglais correspondant
    n'existe, si l'oeuvre est exclue, ou si le fichier est introuvable/illisible."""
    zoo_folder = os.path.basename(os.path.dirname(non_english_file_path))
    num = get_witness_number(non_english_file_path)
    cache_key = f"{zoo_folder}/{num}"
    if cache_key in ENGLISH_WITNESS_EXCLUDE:
        return None
    if cache_key in _english_alignment_cache:
        return _english_alignment_cache[cache_key]

    eng_filename = find_english_witness_file(non_english_file_path)
    out_map = None
    if eng_filename:
        en_path = os.path.join(os.path.dirname(non_english_file_path), eng_filename)
        try:
            with open(en_path, "r", encoding="UTF-8") as f:
                soup = bs(f, "lxml-xml")
            out_map = {}
            _walk_english_paragraphs(soup.body, (), out_map)
        except Exception as e:
            print(f"[WARNING] Echec de la construction de la carte d'alignement anglais pour {en_path}: {e}")
            out_map = None

    _english_alignment_cache[cache_key] = out_map
    return out_map


def report_alignment_stats(file_path):
    """Affiche, pour un fichier non-anglais qui vient d'etre traite, le taux
    de paragraphes ayant effectivement trouve une traduction alignee (vs.
    repli sur Google Translate) - permet de reperer une oeuvre au taux
    anormalement bas (meme diagnostic que le cas Strabon, voir
    ENGLISH_WITNESS_EXCLUDE) sans avoir eu besoin de le mesurer a l'avance."""
    stats = _alignment_stats.get(file_path)
    if not stats or (stats["hits"] + stats["misses"]) == 0:
        return
    total = stats["hits"] + stats["misses"]
    rate = stats["hits"] / total
    flag = " <-- taux bas, a verifier" if 0 < rate < 0.15 else ""
    print(f"[ALIGNEMENT] {file_path} : {stats['hits']}/{total} paragraphes ({rate:.0%}) via traduction humaine alignee{flag}")


def get_aligned_translation(file_path, parent_uri, paragraph_index=None, allow_coarser=True):
    """Cherche, pour un chemin de division non-anglais (ex: '.../g/1/1'), le
    texte anglais deja traduit humainement correspondant, en repliant les
    sous-niveaux supplementaires d'un cote ou de l'autre sur le niveau commun
    le moins profond (cas Strabon, documente section 20.4/20.6 : un temoin
    peut avoir un niveau de decoupage de plus que l'autre).

    paragraph_index / allow_coarser : quand une division originale contient
    PLUSIEURS <p> (donc plusieurs paragraphes distincts sous un meme
    parent_uri), l'appelant passe l'index 1-base du paragraphe courant et
    allow_coarser=False. On cherche alors uniquement une correspondance a la
    bonne granularite (le meme paragraphe cote anglais, ou l'anglais encore
    plus fin) : le repli vers une division anglaise PLUS GROSSIERE est
    interdit, car il collerait le texte anglais du chapitre entier sur
    chacun de ses paragraphes - c'est exactement le bug de gonflage
    (section 22 : cap de 6000 caracteres qui ne protege que les tres longs
    chapitres ; ici zoo81/1g, zoo71/*, zoo7/*... ont des chapitres courts
    dupliques a l'identique sur 100+ paragraphes). Sans correspondance fine,
    on renvoie None et l'appelant retombe sur Google Translate paragraphe
    par paragraphe."""
    align_map = get_english_alignment_map(file_path)
    if not align_map:
        return None

    stats = _alignment_stats.setdefault(file_path, {"hits": 0, "misses": 0})

    numeric_segments = tuple(int(seg) for seg in parent_uri.split("/") if seg.isdigit())
    if paragraph_index is not None:
        numeric_segments = numeric_segments + (int(paragraph_index),)
    if not numeric_segments:
        stats["misses"] += 1
        return None

    # Toute traduction alignee candidate passe par ce filtre avant d'etre
    # acceptee comme un "hit" : au-dela d'une longueur raisonnable pour UN
    # paragraphe, ce n'est plus un texte correspondant a la bonne granularite
    # mais le signe d'un decalage de structure trop grossier pour etre
    # fiable - ex. zoo80/3g (Hippiatrica Parisina, 1719 paragraphes tous
    # directement sous un seul chapitre "plat", cote grec ET anglais) : le
    # chemin grec et le chemin anglais tombent tous deux sur la MEME division
    # unique (correspondance exacte, donc jamais filtree par le plafond sur
    # le nombre d'entrees regroupees ci-dessous), dont le texte anglais fait
    # a lui seul 114 000 caracteres (le chapitre entier) - colle identique
    # sur chacun des 1719 paragraphes, gonflant le fichier d'annotations a
    # 874 Mo. Mieux vaut aucune traduction alignee (repli sur Google
    # Translate) qu'une traduction fausse dupliquee massivement, quelle que
    # soit la branche qui l'a trouvee. Voir DOCUMENTATION_SYSTEME_ZOO.md
    # section 21.
    MAX_ALIGNED_TEXT_LENGTH = 6000
    MAX_BROADEN_MATCHES = 30

    def candidate_texts():
        """Genere, dans l'ordre de priorite, chaque texte anglais candidat
        pour ce chemin (correspondance exacte, puis regroupement d'entrees
        anglaises plus fines, puis realignement par retrait d'un segment de
        tete). Une strategie qui echoue (aucune entree trouvee) passe
        silencieusement a la suivante, et une strategie qui TROUVE une entree
        trop longue (rejetee plus loin par le plafond de longueur) ne doit
        pas non plus empecher d'essayer les strategies restantes : avant le
        correctif de la section 22, un premier essai trouve mais rejete pour
        longueur (ex. zoo25, chapitre anglais de 17 000 caracteres) faisait
        abandonner la recherche au lieu de continuer."""
        if numeric_segments in align_map:
            yield align_map[numeric_segments]

        # Notre chemin est moins profond que l'anglais (ex: grec 1/1/5 ->
        # anglais 1/1/5/1, 1/1/5/2... regroupes en un seul texte). Plafonne
        # aussi le nombre d'entrees regroupees : au-dela, ce n'est plus
        # l'anglais qui subdivise un peu plus finement une meme division
        # (cas legitime, une poignee de sous-parties), mais un vrai
        # decalage de structure.
        matches = [text for path, text in align_map.items()
                   if len(path) > len(numeric_segments)
                   and path[:len(numeric_segments)] == numeric_segments]
        if matches and len(matches) <= MAX_BROADEN_MATCHES:
            yield " ".join(matches)

        # A partir d'ici, on realigne le chemin en retirant UN segment de tete.
        # Interdit quand la division originale porte plusieurs paragraphes
        # (allow_coarser=False) : chaque <p> du chapitre serait sinon associe
        # a une division anglaise sans rapport (bug de gonflage - meme jeu
        # d'annotations sur tous les paragraphes).
        if not allow_coarser:
            return

        # Notre chemin a UN segment de tete que l'anglais n'a pas : soit un
        # vrai numero de livre (zoo25, Isidore - le latin garde "12/3" alors
        # que le temoin anglais, extrait pour ce seul livre, numerote
        # directement ses chapitres "3"), soit une enveloppe structurelle
        # jamais comptee cote anglais mais encore presente cote original
        # (zoo42, Platon Timee - chapitre (1, N) ou le "1" de tete est le
        # <div type="edition" n="urn:cts:..."> ; cf. _walk_english_paragraphs
        # qui, lui, ne le compte pas). On retire donc exactement un segment de
        # tete et on exige une correspondance EXACTE sur le reste : c'est un
        # realignement 1:1 (toujours une division precise), pas un repli.
        #
        # On ne retire volontairement qu'UN seul segment, et on ne replie
        # PLUS sur un prefixe moins profond (ancien "repli de profondeur",
        # retire section 23) : ces deux strategies, sur un chemin a 3 niveaux
        # + enveloppe (ex. zoo8 Oppien, zoo7/1g,5g,6g Aristote), faisaient
        # correspondre la section s de chaque chapitre au chapitre anglais s
        # (ou pire, au tout premier chapitre anglais via (1,)), collant le
        # meme jeu d'annotations sur des dizaines de paragraphes. En l'absence
        # de correspondance fiable ici, mieux vaut le repli sur Google
        # Translate paragraphe par paragraphe. Voir sections 22 et 23.
        if len(numeric_segments) >= 2:
            suffix = numeric_segments[1:]
            if suffix in align_map:
                yield align_map[suffix]

    for text in candidate_texts():
        if text and len(text) <= MAX_ALIGNED_TEXT_LENGTH:
            stats["hits"] += 1
            return text

    stats["misses"] += 1
    return None


def extract_paragraph(parent_division, parent_data, parent_uri, link_data, paragraph_data, annotation_data):

    paragraph_author = ""
    paragraph_work = ""

    if len(parent_division.find_all(["cit"], recursive=False)) >= 1:
        for cit_id, cit_tag in enumerate(parent_division.find_all(["cit"], recursive=False), 1):
            paragraph_id = cit_id

            paragraph_author = cit_tag.bibl.author.text if cit_tag.bibl and cit_tag.bibl.author else "Missing author"
            paragraph_work = cit_tag.bibl.ref.text if cit_tag.bibl and cit_tag.bibl.ref else "Missing work"

            for quote in cit_tag.find_all(["quote"], recursive=False):
                paragraph_text = strip_paragraph_text(quote.text)

                if quote.head:
                    paragraph_title = strip_paragraph_text(quote.head.text)
                else:
                    paragraph_title = ""

                if ANNOTATION_AUTO:
                    if is_english_file(FILE):
                        translated_paragraph = paragraph_text
                    else:
                        translated_paragraph = split_and_translate(paragraph_text, "en")

                    find_thesaurus_entities(translated_paragraph, annotation_data, f"{parent_uri}/text/{paragraph_id}")
                    wikidata_entities = get_NER_from_wikidata(translated_paragraph)
                    extract_wikidata(wikidata_entities, annotation_data, f"{parent_uri}/text/{paragraph_id}")
                    dbpedia_entities = get_NER_from_dbpedia(translated_paragraph)
                    extract_dbpedia(dbpedia_entities, annotation_data, f"{parent_uri}/text/{paragraph_id}")

                # ["parent_uri", "type", "id", "title", "child"]
                link_data.append(
                    [parent_data[0], parent_data[1], parent_data[2], parent_data[3], f"{parent_uri}/text/{paragraph_id}"])
                # ["parent_uri", "type", "id", "title", "text"]
                paragraph_data.append([parent_uri, "Paragraph", paragraph_id, paragraph_title, paragraph_text, paragraph_author, paragraph_work])

    elif len(parent_division.find_all(["p"])) == 0:
        for p_id, p in tqdm(enumerate(parent_division.find_all(["l"], recursive=False), 1)):

            paragraph_id = p_id
            paragraph_text = strip_paragraph_text(p.text)

            if ANNOTATION_AUTO:

                if is_english_file(FILE):
                    translated_paragraph = paragraph_text
                else:
                    translated_paragraph = split_and_translate(paragraph_text, "en")

                find_thesaurus_entities(translated_paragraph, annotation_data, f"{parent_uri}/text/{paragraph_id}")
                wikidata_entities = get_NER_from_wikidata(translated_paragraph)
                extract_wikidata(wikidata_entities, annotation_data, f"{parent_uri}/text/{paragraph_id}")
                dbpedia_entities = get_NER_from_dbpedia(translated_paragraph)
                extract_dbpedia(dbpedia_entities, annotation_data, f"{parent_uri}/text/{paragraph_id}")

            if p.head:
                paragraph_title = strip_paragraph_text(p.head.text)
            else:
                paragraph_title = ""
            # ["parent_uri", "type", "id", "title", "child"]
            link_data.append([parent_data[0], parent_data[1], parent_data[2], parent_data[3], f"{parent_uri}/text/{paragraph_id}"])
            # ["parent_uri", "type", "id", "title", "text"]
            paragraph_data.append([parent_uri, "Paragraph", paragraph_id, paragraph_title, paragraph_text, paragraph_author, paragraph_work])
    else:
        p_id = 1
        # recursive=False: ce div peut lui-meme avoir des div enfants (voir le
        # nouvel appel a extract_paragraph() pour les div "mixtes" dans
        # extract_division_metadata) ; sans ca, find_all(["p"]) redescend dans
        # ces div enfants et retraite leurs <p>, qui seront de toute facon
        # correctement extraits par le prochain appel recursif sur ce div
        # enfant - doublon silencieux sinon.
        direct_ps = [pp for pp in parent_division.find_all(["p"], recursive=False)
                     if not pp.find_parent('p') and strip_text(pp.text) != ""]
        # Cette division a-t-elle plusieurs paragraphes distincts ? Si oui, la
        # traduction alignee doit se faire paragraphe par paragraphe (jamais
        # coller le texte anglais de toute la division sur chacun) - voir
        # get_aligned_translation().
        multi_paragraph_division = len(direct_ps) > 1
        for p in tqdm(parent_division.find_all(["p"], recursive=False)):
            if not p.find_parent('p'):
                if strip_text(p.text) == "":
                    continue

                if p.head:
                    paragraph_title = strip_paragraph_text(p.head.text)
                else:
                    paragraph_title = ""

                if parent_data[1] == "BekkerPage":
                    paragraph_id = 0 if "a" in parent_data[3] else 1
                    paragraph_text = strip_paragraph_text(p.text)
                    if ANNOTATION_AUTO:
                        if is_english_file(FILE):
                            translated_paragraph = paragraph_text
                        else:
                            aligned = get_aligned_translation(FILE, parent_uri)
                            translated_paragraph = aligned if aligned else split_and_translate(paragraph_text, "en")

                        find_thesaurus_entities(translated_paragraph, annotation_data, f"{parent_uri}/text/{paragraph_id}")
                        wikidata_entities = get_NER_from_wikidata(translated_paragraph)
                        extract_wikidata(wikidata_entities, annotation_data, f"{parent_uri}/text/{paragraph_id}")
                        dbpedia_entities = get_NER_from_dbpedia(translated_paragraph)
                        extract_dbpedia(dbpedia_entities, annotation_data, f"{parent_uri}/text/{paragraph_id}")

                    # ["parent_uri", "type", "id", "title", "child"]
                    link_data.append([parent_data[0], parent_data[1], parent_data[2], parent_data[2],
                                      f"{parent_uri}/text/{paragraph_id}"])
                    # ["parent_uri", "type", "id", "title", "text"]
                    paragraph_data.append([parent_uri, "Paragraph", paragraph_id, paragraph_title, paragraph_text, paragraph_author, paragraph_work])
                else:
                    paragraph_id = p_id
                    paragraph_text = strip_paragraph_text(p.text)

                    if ANNOTATION_AUTO:
                        if is_english_file(FILE):
                            translated_paragraph = paragraph_text
                        else:
                            aligned = get_aligned_translation(
                                FILE, parent_uri,
                                paragraph_index=paragraph_id if multi_paragraph_division else None,
                                allow_coarser=not multi_paragraph_division,
                            )
                            translated_paragraph = aligned if aligned else split_and_translate(paragraph_text, "en")

                        find_thesaurus_entities(translated_paragraph, annotation_data, f"{parent_uri}/text/{paragraph_id}")
                        wikidata_entities = get_NER_from_wikidata(translated_paragraph)
                        extract_wikidata(wikidata_entities, annotation_data ,f"{parent_uri}/text/{paragraph_id}" )
                        dbpedia_entities = get_NER_from_dbpedia(translated_paragraph)
                        extract_dbpedia(dbpedia_entities, annotation_data ,f"{parent_uri}/text/{paragraph_id}" )

                    # ["parent_uri", "type", "id", "title", "child"]
                    link_data.append([parent_data[0], parent_data[1], parent_data[2], parent_data[3], f"{parent_uri}/text/{paragraph_id}"])
                    # ["parent_uri", "type", "id", "title", "text"]
                    paragraph_data.append([parent_uri, "Paragraph", paragraph_id, paragraph_title, paragraph_text, paragraph_author, paragraph_work])
                    p_id += 1
    try:
        return paragraph_id, paragraph_text
    except UnboundLocalError:
        print("Paragraph_id and paragraph_text is not defined")

# zoo4 (Antigonus) et zoo89 (Pseudo-Aristote) ne retiennent que le sous-ensemble
# zoologique de chapitres de leur oeuvre source (98/173 et 72/178) : leurs n=
# ont donc des trous (1,2,3,4,6,7...). extract_division_metadata utilise par
# defaut la position (1er, 2e, 3e div...) plutot que n= pour construire l'URI
# (cf. tag_div_id ci-dessous) - sans consequence tant que n= suit la position
# sans trou, ce qui etait toujours le cas jusqu'a ces deux oeuvres. Avec des
# trous, position et n= divergent : l'URI d'un chapitre ne correspond plus a
# son vrai numero (le champ 'title' reste correct, lui, donc rien de faux ne
# s'affichait cote appli, mais toute recherche/lien futur qui deduirait le
# numero de chapitre depuis l'URI serait silencieusement faux). Fix cible
# a ces deux dossiers plutot qu'une bascule generale sur n= pour tout le
# corpus, qui changerait l'URI de chaque chapitre deja publie ailleurs.
GAPPED_CHAPTER_NUMBERING_FOLDERS = {"zoo4", "zoo89", "zoo14"}


def compute_div_id(tag_div, tag_id, tag_div_type, zoo_folder=None):
    """Identifiant utilise dans l'URI pour ce div : le numero de page Bekker
    s'il y en a un, sinon n= pour les dossiers a numerotation trouee
    (GAPPED_CHAPTER_NUMBERING_FOLDERS), sinon la position (comportement
    d'origine). Factorise pour rester coherent entre le calcul de l'id du
    div courant et les URI enfants pre-listees avant la recursion."""
    if tag_div_type == "BekkerPage":
        return int(re.search(r"\d+", tag_div["n"]).group())
    if (zoo_folder in GAPPED_CHAPTER_NUMBERING_FOLDERS and tag_div.has_attr("n")
            and tag_div["n"].isdigit()):
        return int(tag_div["n"])
    return tag_id


def get_div_type(tag_div):
    div_type_attr = tag_div.get("type", "")
    if div_type_attr and "textpart" not in div_type_attr and not any(c.isnumeric() for c in div_type_attr):
        return div_type_attr.title().replace(" ", "")
    fallback_attr = tag_div.get("subtype", "") or div_type_attr or tag_div.name
    return fallback_attr.title().replace(" ", "")


def extract_division_metadata(div, parent_uri, link_data, paragraph_data, annotation_data, depth, zoo_folder=None):
    for tag_id, tag_div in tqdm(enumerate(div.find_all(re.compile("^div"), recursive=False), 1)):
        tag_div_type = get_div_type(tag_div)
        tag_div_id = compute_div_id(tag_div, tag_id, tag_div_type, zoo_folder)

        if tag_div.find_all("head", recursive=False):
            tag_div_title = strip_text(tag_div.head.text)
        else:
            tag_div_title = tag_div["n"] if tag_div.has_attr("n") else tag_div_id

        current_uri = f"{parent_uri}/{tag_div_id}"

        # if still div remaining
        if does_it_have_children_div(tag_div):
            if tag_div_type == "Oeuvre":
                for child_tag_id, child_div in enumerate(tag_div.find_all(re.compile("^div"), recursive=False), 1):
                    child_id = compute_div_id(child_div, child_tag_id, get_div_type(child_div), zoo_folder)
                    link_data.append([parent_uri, tag_div_type, tag_div_id, tag_div_title, f"{parent_uri}/{child_id}"])
                extract_division_metadata(tag_div, parent_uri, link_data, paragraph_data, annotation_data, depth + 1, zoo_folder)
                continue

            if depth == 0:
                link_data.append([parent_uri, "Work", tag_div_id, tag_div_title, f"{parent_uri}/{tag_div_id}"])

            # extract quote if there are quotes
            if len(tag_div.find_all(["cit"], recursive=False)) > 1:
                extract_paragraph(tag_div,
                                  [parent_uri,
                                   tag_div_type, tag_id, tag_div_title],
                                  current_uri, link_data, paragraph_data, annotation_data)

            # ce div a des div enfants (branche does_it_have_children_div), mais
            # peut aussi porter ses propres <p> directs (ex: une ligne
            # d'attribution "Par Apsyrtus." posee directement dans un div
            # "chapter" juste avant ses div "section" enfants). Sans cet appel,
            # extract_paragraph() n'etait jamais invoque pour ce div (seule la
            # recursion sur les div enfants ci-dessous l'etait), et ces <p>
            # directs disparaissaient silencieusement de l'extraction - bug
            # decouvert sur zoo80/2e (Hippiatrica Berolinensia, structure
            # imbriquee jusqu'a 7 niveaux), 285 paragraphes concernes sur 3047.
            elif tag_div.find_all(["p"], recursive=False):
                extract_paragraph(tag_div,
                                  [parent_uri,
                                   tag_div_type, tag_id, tag_div_title],
                                  current_uri, link_data, paragraph_data, annotation_data)

            for child_tag_id, child_div in enumerate(tag_div.find_all(re.compile("^div"), recursive=False),1):
                # ["parent_uri", "type", "id", "title", "child"]
                child_id = compute_div_id(child_div, child_tag_id, get_div_type(child_div), zoo_folder)
                link_data.append([parent_uri, tag_div_type, tag_div_id, tag_div_title, f"{current_uri}/{child_id}"])
            extract_division_metadata(tag_div, current_uri, link_data, paragraph_data, annotation_data, depth + 1, zoo_folder)
        else:
            if depth == 0:
                link_data.append([parent_uri, "Oeuvre", tag_div_id, tag_div_title, f"{parent_uri}/{tag_div_id}"])
            extract_paragraph(tag_div,[parent_uri, tag_div_type, tag_div_id, tag_div_title],current_uri, link_data, paragraph_data, annotation_data)


def sanitize_iri_component(text):
    """Retire les caracteres invalides ou problematiques dans une IRI (RFC 3987
    + caracteres qui font echouer silencieusement la generation RDF en aval,
    ex: apostrophe dans "De l'equitation"), ex: < > " { } | \\ ^ ` '
    Le titre affiche (champ 'title') n'est pas touche, seul le segment d'URI l'est."""
    return re.sub(r'[<>"{}|\\^`\']', '', text)


def extraction_data(FILE,CSV):
    with (open(FILE, 'r', encoding="UTF-8") as xml_file):

        xml_parser = bs(xml_file, "lxml-xml")
        oeuvre_id, oeuvre_title, author, date, editor = extract_sourcedesc_data(xml_parser)
        zoo_folder = os.path.basename(os.path.dirname(FILE))
        author = CANONICAL_AUTHORS.get(zoo_folder, author)
        body_parser = xml_parser.body
        # translate author and oeuvre_id
        link_data = []
        link_labels = ["parent_uri", "type", "id", "title", "child"]
        paragraph_data = []
        paragraph_labels = ["parent_uri", "type", "id", "title", "text", "author", "work"]
        metadata_labels = ["uri", "id", "type", "title", "author", "date", "editor", "prov"]
        annotation_data = []
        annotation_labels = ["paragraph_uri", "concept_uri", "mention", "score", "origin"]

        text_tag = xml_parser.find("text")
        # Derive de la convention de nommage (fiable) plutot que de l'attribut
        # xml:lang du XML (souvent absent). Sans ca, deux temoins d'une meme
        # oeuvre dans des langues differentes (ex: grec + traduction anglaise)
        # peuvent finir avec la meme URI si xml:lang est absent des deux cotes,
        # ce qui fusionne a tort leurs structures internes (chapitres, etc.)
        # et peut creer un cycle parent/enfant cote appli web.
        lang_suffix = get_witness_lang(FILE) + get_witness_suffix(FILE)
        # zoo4/1g.xml (TLG, licence restreinte, EN ATTENTE) et zoo4/2g.xml
        # (Keller 1877, domaine public) sont deux temoins grecs distincts du
        # meme titre - meme probleme de collision d'URI que Grattius/zoo20
        # ci-dessous, mais avec des numeros de temoin differents (1 vs 2)
        # plutot qu'un suffixe _N partage : get_witness_suffix() ne les
        # detecte donc pas comme "siblings". Fix cible plutot que d'elargir
        # cette fonction a tout le corpus (trop de risque de deplacer des
        # URI deja publiees ailleurs).
        ZOO4_WITNESS_SUFFIXES = {"1g.xml": "_1", "2g.xml": "_2"}
        if zoo_folder == "zoo4" and os.path.basename(FILE) in ZOO4_WITNESS_SUFFIXES:
            lang_suffix += ZOO4_WITNESS_SUFFIXES[os.path.basename(FILE)]
        # Le nom canonique (CANONICAL_AUTHORS) est deja propre: pas besoin de le
        # faire passer par Google Translate (meme risque de corruption que le
        # Bug 6 sur les titres). On ne traduit que si aucune forme canonique
        # n'a ete trouvee (repli sur le texte brut extrait du XML).
        author_uri_segment = author if zoo_folder in CANONICAL_AUTHORS else clean_uri(author)
        uri = f"http://ns.inria.fr/zoomathia/{sanitize_iri_component(author_uri_segment.replace(' ', '_'))}/{sanitize_iri_component(oeuvre_id)}/{lang_suffix}"

        # zoo20/1l_1 et 1l_2 sont deux editions de Cynegetica (Grattius) au
        # titre identique : sans ca, elles seraient indiscernables dans les
        # menus "Work" de l'appli (voir aussi get_witness_suffix ci-dessus,
        # qui evite deja qu'elles partagent la meme URI).
        EDITION_LABELS = {
            "1l_1.xml": " (ed. Haupt 1838)",
            "1l_2.xml": " (ed. The Latin Library)",
            "1e.xml": " (trad. Duff & Duff, Loeb 1935)",
        }
        if zoo_folder == "zoo20" and os.path.basename(FILE) in EDITION_LABELS:
            oeuvre_title += EDITION_LABELS[os.path.basename(FILE)]

        ZOO4_EDITION_LABELS = {
            "1g.xml": " (TLG - EN ATTENTE, licence restreinte)",
            "2g.xml": " (ed. Keller 1877)",
        }
        if zoo_folder == "zoo4" and os.path.basename(FILE) in ZOO4_EDITION_LABELS:
            oeuvre_title += ZOO4_EDITION_LABELS[os.path.basename(FILE)]

        metadata = [[uri, oeuvre_id, "Oeuvre", oeuvre_title, author, date, editor, FILE]]

        extract_division_metadata(body_parser, uri, link_data, paragraph_data,annotation_data, 0, zoo_folder)
        report_alignment_stats(FILE)

        pd.DataFrame(link_data, columns=link_labels).to_csv('./output/' + CSV + "_link.csv", index=False,
                                                            encoding='UTF-8')
        pd.DataFrame(paragraph_data, columns=paragraph_labels).to_csv('./output/' + CSV + "_paragraph.csv", index=False,
                                                                      encoding='UTF-8')
        pd.DataFrame(metadata, columns=metadata_labels).to_csv('./output/' + CSV + "_metadata.csv", index=False,
                                                     encoding='UTF-8')
        pd.DataFrame(annotation_data, columns=annotation_labels).to_csv('./output/' + CSV + "_annotations.csv",index=False)


def get_all_thesaurus_concepts(g):
    q = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT ?concept ?label WHERE { 
            ?concept a skos:Concept ;
                     skos:prefLabel ?label .
            FILTER(lang(?label) = "en")
        }
        """

    res = convert_sparql_to_json(sparqlQuery(g, q))
    thesaurus_dict = {}

    for item in res["results"]["bindings"]:
        concept_uri = item["concept"]["value"]
        entity_label = item["label"]["value"]

        thesaurus_dict[entity_label] = concept_uri

    return thesaurus_dict

def _worker_init():
    """Prepare chaque processus worker du Pool. Le gateway JVM (Corese)
    n'est en fait utilise qu'une seule fois, au demarrage du script
    principal, pour charger le thesaurus (th310.ttl) et construire
    matcher/thesaurus_dict AVANT la creation du Pool - extraction_data()
    et tout ce qu'elle appelle (traduction, NER, ecriture CSV) ne s'en
    servent jamais. Sur Linux, fork() copie ces objets deja construits
    (nlp_model, matcher, thesaurus_dict) dans chaque worker sans cout
    de rechargement - mais il copie aussi l'etat `atexit` du parent, y
    compris l'arret du gateway JVM partage. Sans ce correctif, le
    PREMIER worker a se terminer eteindrait le gateway pour tout le
    monde (y compris le processus principal, si jamais il en avait
    encore besoin) : on desenregistre donc cet arret dans les workers,
    seul le processus principal doit l'executer."""
    atexit.unregister(exit_handler)


def process_one_file(xml_file):
    """Traite un fichier XML de bout en bout (validation TEI, extraction,
    traduction, NER, ecriture CSV) et retourne un statut plutot que de
    modifier des listes partagees - necessaire pour tourner dans un
    processus separe du Pool (point 2 "amelioration du pipeline" :
    paralleliser xml_to_csv.py). Statuts : "skip", "invalid", "failed",
    "ok".

    `global FILE` : extract_paragraph() (et d'autres fonctions plus bas
    dans la chaine d'appel) lisent FILE comme variable GLOBALE du module
    plutot que de la recevoir en parametre - c'etait deja le cas avant
    la parallelisation (FILE = xml_file etait affecte directement dans
    la boucle du bloc __main__, donc au niveau module). Sans ce `global`
    ici, cette affectation resterait locale a process_one_file() et le
    reste de la chaine d'appel leverait un NameError. Sans danger avec
    des processus separes (multiprocessing) : chaque worker a son propre
    espace memoire issu du fork, aucun partage ni race condition entre
    eux - ce serait different avec des threads."""
    global FILE
    FILE = xml_file
    if not os.path.exists(FILE):
        return ("skip", xml_file, "fichier supprime depuis le lancement")

    zoo_folder = os.path.basename(os.path.dirname(FILE))
    CSV = zoo_folder + "_" + ".".join(os.path.basename(FILE).split(".")[0:-1])

    meta_path = './output/' + CSV + "_metadata.csv"
    if os.path.exists(meta_path) and os.path.getmtime(meta_path) >= os.path.getmtime(FILE):
        return ("skip", xml_file, "deja traite, a jour")

    print(xml_file, flush=True)

    # Validation TEI P5 en amont (point 1 "amelioration du pipeline") :
    # rejeter un XML mal forme ou non conforme AVANT extraction/
    # traduction/NER, plutot que de decouvrir le probleme au bout de
    # plusieurs heures de traitement.
    tei_ok, tei_errors = validate_tei_file(FILE)
    if not tei_ok:
        print(f"INVALIDE (non conforme TEI P5) sur {xml_file}, fichier saute :", flush=True)
        for err in tei_errors[:5]:
            print(f"    {err}", flush=True)
        return ("invalid", xml_file, tei_errors[:5])

    try:
        extraction_data(FILE, CSV)
    except Exception:
        print(f"ECHEC sur {xml_file}, fichier saute, lot poursuivi :", flush=True)
        traceback.print_exc()
        return ("failed", xml_file, traceback.format_exc())

    return ("ok", xml_file, None)


if __name__ == "__main__":

    g = Graph()
    g = load(g, "th310.ttl")

    thesaurus_dict = get_all_thesaurus_concepts(g)

    matcher = PhraseMatcher(nlp_model.vocab, attr="LEMMA")
    for concept_name in thesaurus_dict.keys():
        matcher.add(concept_name, [nlp_model(concept_name)])

    # Argument optionnel : soit un entier (nombre max de fichiers a traiter
    # dans cet appel, pour faire passer le corpus par lots et verifier le
    # resultat entre deux lots), soit le chemin d'un fichier texte listant
    # des chemins XML precis a traiter (un par ligne, relatifs a ce dossier),
    # pour cibler un sous-ensemble plutot que tout ./zoo/. Dans les deux cas
    # les fichiers deja a jour sont sautes via le test de mtime dans
    # process_one_file().
    batch_limit = None
    xml_files = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            with open(arg, encoding="utf-8") as f:
                xml_files = [line.strip() for line in f if line.strip()]
        else:
            batch_limit = int(arg)

    if xml_files is None:
        directory_path = ('./zoo/')
        xml_files = sorted(find_xml_files(directory_path))

    if batch_limit is not None:
        xml_files = xml_files[:batch_limit]

    # Parallelisme borne (point 2 "amelioration du pipeline") : le
    # goulot d'etranglement reel n'est pas le CPU mais Google Translate,
    # dont la limitation de debit se declenche cote serveur externe,
    # independamment du nombre de coeurs locaux - au-dela de quelques
    # traductions simultanees, on risque surtout de declencher le
    # blocage plus vite sans gagner de temps. D'ou un pool volontairement
    # petit (3-4, pas "un par coeur") plutot qu'un plafond ambitieux.
    # Reglable via la variable d'environnement ZOO_XML2CSV_WORKERS pour
    # experimenter sans modifier le code.
    n_workers = int(os.environ.get("ZOO_XML2CSV_WORKERS", "4"))

    if n_workers > 1:
        # Le gateway JVM (py4j) n'est plus necessaire a partir d'ici -
        # extraction_data() et tout ce qu'elle appelle ne s'en servent
        # jamais (seul le chargement du thesaurus ci-dessus en avait
        # besoin). Le fermer AVANT de forker les workers du Pool est
        # imperatif : py4j maintient une connexion/thread en arriere-plan,
        # et fork() ne duplique que le thread appelant - un thread interne
        # py4j resterait dans un etat incoherent dans chaque worker,
        # source de blocages silencieux observes empiriquement (un
        # fichier de 7 paragraphes reste bloque plus de 30 min sans
        # jamais lever d'exception, alors que le pire cas attendu avec
        # les reessais de traduction est de l'ordre de 7 minutes).
        exit_handler()

    processed = 0
    failed = []
    invalid_tei = []
    skipped = 0

    if n_workers <= 1:
        results = (process_one_file(f) for f in xml_files)
    else:
        pool = multiprocessing.Pool(processes=n_workers, initializer=_worker_init)
        results = pool.imap_unordered(process_one_file, xml_files)

    for status, xml_file, detail in results:
        if status == "skip":
            print(f"Skip ({detail}): {xml_file}")
            skipped += 1
        elif status == "invalid":
            invalid_tei.append(xml_file)
        elif status == "failed":
            failed.append(xml_file)
        else:
            processed += 1

    if n_workers > 1:
        pool.close()
        pool.join()

    print("End of CSV generation")
    if invalid_tei:
        print(f"{len(invalid_tei)} fichier(s) rejete(s) pour non-conformite TEI P5 :")
        for f in invalid_tei:
            print(f"  - {f}")
    if failed:
        print(f"{len(failed)} fichier(s) en echec :")
        for f in failed:
            print(f"  - {f}")
