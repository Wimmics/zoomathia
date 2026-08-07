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
from spacy.matcher import PhraseMatcher
from spacy.lang.en.stop_words import STOP_WORDS

java_process = subprocess.Popen(
    ['java', '-jar', '-Dfile.encoding=UTF-8', 'corese-library-python-4.4.1.jar'])
sleep(6)
gateway = JavaGateway()

def exit_handler():
    gateway.shutdown()
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

def split_and_translate(text, lang_target, max_chunk_length=1000):
    chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
    translated_chunks = []

    for chunk in chunks:
        tries = 0
        success = False
        while not success:
            try:
                translated_chunk = GoogleTranslator(source='auto', target=lang_target).translate(chunk)
                if translated_chunk is not None:
                    translated_chunks.append(translated_chunk)

                success = True

            except Exception as e:
                tries += 1
                wait = min(5 * tries, 60)
                print(f" Echec connexion à Google Translate (Tentative {tries}). Reessai dans {wait}s...")
                time.sleep(wait)

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
    "../../repertoire_zoo/repertoire_codes_zoo.csv",
    "../../repertoire_codes_zoo.csv",
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
        translated_txt = GoogleTranslator(source='auto', target="en").translate(txt)
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
        for p in tqdm(parent_division.find_all(["p"])):
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
                            translated_paragraph = split_and_translate(paragraph_text, "en")

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
                            translated_paragraph = split_and_translate(paragraph_text, "en")

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

def extract_division_metadata(div, parent_uri, link_data, paragraph_data, annotation_data, depth):
    for tag_id, tag_div in tqdm(enumerate(div.find_all(re.compile("^div"), recursive=False), 1)):
        div_type_attr = tag_div.get("type", "")
        if div_type_attr and "textpart" not in div_type_attr and not any(c.isnumeric() for c in div_type_attr):
            tag_div_type = div_type_attr.title().replace(" ", "")
        else:
            fallback_attr = tag_div.get("subtype", "") or div_type_attr or tag_div.name
            tag_div_type = fallback_attr.title().replace(" ", "")

        if tag_div_type == "BekkerPage":
            # extract number from the title
            tag_div_id = int(re.search(r"\d+", tag_div["n"]).group())
        else:
            tag_div_id = tag_id

        if tag_div.find_all("head", recursive=False):
            tag_div_title = strip_text(tag_div.head.text)
        else:
            tag_div_title = tag_div["n"] if tag_div.has_attr("n") else tag_div_id

        current_uri = f"{parent_uri}/{tag_div_id}"

        # if still div remaining
        if does_it_have_children_div(tag_div):
            if tag_div_type == "Oeuvre":
                for child_id, _ in enumerate(tag_div.find_all(re.compile("^div"), recursive=False), 1):
                    link_data.append([parent_uri, tag_div_type, tag_div_id, tag_div_title, f"{parent_uri}/{child_id}"])
                extract_division_metadata(tag_div, parent_uri, link_data, paragraph_data, annotation_data, depth + 1)
                continue

            if depth == 0:
                link_data.append([parent_uri, "Work", tag_div_id, tag_div_title, f"{parent_uri}/{tag_div_id}"])

            # extract quote if there are quotes
            if len(tag_div.find_all(["cit"], recursive=False)) > 1:
                extract_paragraph(tag_div,
                                  [parent_uri,
                                   tag_div_type, tag_id, tag_div_title],
                                  current_uri, link_data, paragraph_data, annotation_data)

            for child_id, _ in enumerate(tag_div.find_all(re.compile("^div"), recursive=False),1):
                # ["parent_uri", "type", "id", "title", "child"]
                link_data.append([parent_uri, tag_div_type, tag_div_id, tag_div_title, f"{current_uri}/{child_id}"])
            extract_division_metadata(tag_div, current_uri, link_data, paragraph_data, annotation_data, depth + 1)
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
        lang_suffix = get_witness_lang(FILE)
        # Le nom canonique (CANONICAL_AUTHORS) est deja propre: pas besoin de le
        # faire passer par Google Translate (meme risque de corruption que le
        # Bug 6 sur les titres). On ne traduit que si aucune forme canonique
        # n'a ete trouvee (repli sur le texte brut extrait du XML).
        author_uri_segment = author if zoo_folder in CANONICAL_AUTHORS else clean_uri(author)
        uri = f"http://ns.inria.fr/zoomathia/{sanitize_iri_component(author_uri_segment.replace(' ', '_'))}/{sanitize_iri_component(oeuvre_id)}/{lang_suffix}"

        metadata = [[uri, oeuvre_id, "Oeuvre", oeuvre_title, author, date, editor, FILE]]

        extract_division_metadata(body_parser, uri, link_data, paragraph_data,annotation_data, 0)

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

if __name__ == "__main__":

    g = Graph()
    g = load(g, "th310.ttl")

    thesaurus_dict = get_all_thesaurus_concepts(g)

    matcher = PhraseMatcher(nlp_model.vocab, attr="LEMMA")
    for concept_name in thesaurus_dict.keys():
        matcher.add(concept_name, [nlp_model(concept_name)])

    directory_path = ('./zoo/')
    xml_files = find_xml_files(directory_path)
    for xml_file in xml_files:

        FILE = xml_file
        zoo_folder = os.path.basename(os.path.dirname(FILE))
        CSV = zoo_folder + "_" + ".".join(os.path.basename(FILE).split(".")[0:-1])

        meta_path = './output/' + CSV + "_metadata.csv"
        if os.path.exists(meta_path) and os.path.getmtime(meta_path) >= os.path.getmtime(FILE):
            print(f"Skip (deja traite, a jour): {xml_file}")
            continue

        print(xml_file)
        extraction_data(FILE, CSV)

    print("End of CSV generation")
