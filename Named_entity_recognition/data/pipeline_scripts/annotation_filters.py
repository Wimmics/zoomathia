"""Filtres appliques aux annotations avant leur ecriture (xml_to_csv.py) ou leur
chargement (morph_mongo.py), et utilisables a posteriori sur MongoDB
(apply_annotation_filters.py).

Ils sont nes de la relecture manuelle d'un echantillon de 200 annotations
(documentation, section 26.7) : DBpedia relie des mots courants a des pages sans
rapport ("revolving" -> Revolver), des numeros de notes et de sections sont pris
pour des entites (42, XIX), et quelques concepts du thesaurus sont polysemiques
("led" -> Lead, le metal). Ce sont des regles simples, a discuter avec l'equipe.
"""
import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_NUMBER = re.compile(r'^[\dIVXLCDM]+$')
_IRREGULAR = {'men': 'man', 'women': 'woman', 'children': 'child', 'feet': 'foot',
              'mice': 'mouse', 'geese': 'goose', 'teeth': 'tooth'}


def _load_json(name, default):
    path = os.path.join(_HERE, name)
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


_EXCLUSIONS = _load_json('annotation_exclusions.json', {})
EXCLUDED_THESAURUS_CONCEPTS = set(_EXCLUSIONS.get('thesaurus_concepts', []))
EXCLUDED_THESAURUS_MENTIONS = {k: set(v) for k, v in _EXCLUSIONS.get('thesaurus_mentions', {}).items()}

# Caches remplis par refresh_annotation_caches.py (absents : les regles qui
# s'appuient dessus sont simplement sans effet).
_ALIASES = set(_load_json('dbpedia_aliases.json', {}).get('aliases', []))
_WIKIDATA = _load_json('wikidata_descriptions.json', {})

# Descriptions Wikidata d'entites modernes sans rapport avec les textes anciens
# (films, groupes, marques, villes actuelles, equipes de course...).
_WIKIDATA_NOISE = re.compile(
    r"\b(film|television series|tv series|television show|album|song|single|(rock|ska|pop|metal|hip hop) band|"
    r"musical group|band from|brand|cigarette|manufacturer|aircraft|company|racing|motorsport|auto racing|"
    r"football|footballer|basketball|baseball|cricketer|wrestler|comics? (character|book)|dc comics|marvel|"
    r"fictional character|video game|(town|village|municipality|commune|suburb|hamlet) in|census-designated|"
    r"unincorporated|tram|bus route|route \d+|railway station|disambiguation|given name|family name|surname|"
    r"american (actor|actress|singer|rapper)|record label|magazine|newspaper|website|software|programming language)\b",
    re.I)


def _stems(word):
    word = word.lower()
    out = {word}
    if word in _IRREGULAR:
        out.add(_IRREGULAR[word])
    for suffix, replacement in (('ies', 'y'), ('es', ''), ('s', ''), ('ed', ''),
                                ('d', ''), ('ing', ''), ('ing', 'e')):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            out.add(word[:-len(suffix)] + replacement)
    return out


def _dbpedia_title(uri):
    return re.sub(r'_\(.*\)$', '', uri.rstrip('/').split('/')[-1]).replace('_', ' ').lower()


def _thesaurus_id(uri):
    match = re.search(r'idc=([^&]+)', uri)
    return match.group(1) if match else None


def keep_annotation(concept_uri, mention, origin):
    """True si l'annotation est conservee.
    - une mention reduite a un nombre ou a un chiffre romain n'est jamais gardee ;
    - DBpedia : le titre de la page doit correspondre au mot annote (aux
      variations de forme pres), ou, pour un nom propre, contenir ce mot ;
    - thesaurus : les concepts polysemiques listes dans annotation_exclusions.json
      sont ecartes ;
    - Wikidata : les entites dont la description est un film, un groupe, une marque,
      une ville actuelle, etc. sont ecartees (cache wikidata_descriptions.json).
    - DBpedia : un alias (redirection) connu de la ressource est aussi accepte
      (cache dbpedia_aliases.json)."""
    mention = (mention or '').strip()
    if not mention or _NUMBER.match(mention):
        return False
    if origin == 'DBpedia':
        title = _dbpedia_title(concept_uri)
        if _stems(mention) & _stems(title):
            return True
        if f'{mention.lower()}|{concept_uri}' in _ALIASES:
            return True
        return (mention[:1].isupper() and len(mention) >= 4
                and mention.lower() in title.split() and not re.search(r'\d', title))
    if origin in ('zoomathia', 'zoomathia_match'):
        concept_id = _thesaurus_id(concept_uri)
        if concept_id in EXCLUDED_THESAURUS_CONCEPTS:
            return False
        return mention.lower() not in EXCLUDED_THESAURUS_MENTIONS.get(concept_id, ())
    if origin == 'wikidata':
        entry = _WIKIDATA.get(concept_uri.rstrip('/').split('/')[-1])
        if entry and entry.get('description') and _WIKIDATA_NOISE.search(entry['description']):
            return False
    return True
