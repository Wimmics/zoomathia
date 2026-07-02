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
from google import genai
from pydantic import BaseModel
from google.genai import types
from dotenv import load_dotenv


java_process = subprocess.Popen(
    ['java', '-jar', '-Dfile.encoding=UTF-8', '../corese-library-python-4.4.1.jar'])
sleep(1)
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
API_ENDPOINT_URL = "http://nerd.huma-num.fr/nerd/service"
DBPEDIA_LOCAL = 'http://localhost:2222/rest'

SUPPORTED_DIV = ["poem", "book", "chapter", "section", "edition"]
ANNOTATION_AUTO = True

load_dotenv()
client = genai.Client()
MODEL = "gemini-3.5-flash"
PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompt.txt")

if not os.path.exists(PROMPT_PATH):
    raise FileNotFoundError(f"\n[ERROR] The prompt file hasn't been found at : '{PROMPT_PATH}'")

with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    PROMPT = f.read()

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


def get_LLM_entities(element, lg="en"):
    if not element or element.strip() == "":
        return []

    # Combinaison du prompt de base (contenant les instructions de rôle) et du paragraphe à traiter
    full_input = f"{PROMPT}\n\nTexte à analyser :\n{element}"

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=full_input,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=NERResponse,
            ),
        )

        # Le SDK parse automatiquement le JSON vers l'objet Pydantic via response.parsed
        parsed_data = response.parsed
    except Exception as e:
        print(f"[WARNING] Erreur lors de l'appel LLM ou du parsing : {e}")
        return []

def extract_LLM(entities, annotations, paragraph):
    for ent in entities:
        if ent is None or ent == '':
            continue
        if ent is not None and ent._.nerd_score >= 0.3:

            annotations.append([paragraph,
                                ent._.url_wikidata,
                                ent.text,
                                ent._.nerd_score,
                                MODEL])


def extract_sourcedesc_data(source):
    """
        Extract metadata from XML-TEI header
        *Those information cannot be found in the body*
    """

    date = strip_text(source.sourceDesc.date.text) if source.sourceDesc and source.sourceDesc.date \
        else strip_text(source.titleStmt.date.text) if source.titleStmt and source.titleStmt.date else strip_text(
        source.publicationStmt.date.text) if source.publicationStmt and source.publicationStmt.date else "date not found"
    editor = strip_text(source.titleStmt.editor.text) if source.titleStmt and source.titleStmt.editor else "Unknown editor"
    author = strip_text(source.titleStmt.author.text) if source.titleStmt and source.titleStmt.author else \
        strip_text(
            source.sourceDesc.author.text) if source.sourceDesc and source.sourceDesc.author else 'Author not found'
    oeuvre_title = clean_uri(source.titleStmt.title.text) if source.titleStmt and source.titleStmt.title else "title not found"
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
                    if "eng" in FILE.split("\\")[-1]:
                        translated_paragraph = paragraph_text
                    else:
                        translated_paragraph = split_and_translate(paragraph_text, "en")

                    LLM_entities = get_LLM_entities(translated_paragraph)
                    extract_LLM(LLM_entities, annotation_data,f"{parent_uri}/text/{paragraph_id}")

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

                if "eng" in FILE.split("\\")[-1]:
                    translated_paragraph = paragraph_text
                else:
                    translated_paragraph = split_and_translate(paragraph_text, "en")

                LLM_entities = get_LLM_entities(translated_paragraph)
                extract_LLM(LLM_entities, annotation_data, f"{parent_uri}/text/{paragraph_id}")

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
                        if "eng" in FILE.split("\\")[-1]:
                            translated_paragraph = paragraph_text
                        else:
                            translated_paragraph = split_and_translate(paragraph_text, "en")

                        LLM_entities = get_LLM_entities(translated_paragraph)
                        extract_LLM(LLM_entities, annotation_data, f"{parent_uri}/text/{paragraph_id}")

                    # ["parent_uri", "type", "id", "title", "child"]
                    link_data.append([parent_data[0], parent_data[1], parent_data[2], parent_data[2],
                                      f"{parent_uri}/text/{paragraph_id}"])
                    # ["parent_uri", "type", "id", "title", "text"]
                    paragraph_data.append([parent_uri, "Paragraph", paragraph_id, paragraph_title, paragraph_text, paragraph_author, paragraph_work])
                else:
                    paragraph_id = p_id
                    paragraph_text = strip_paragraph_text(p.text)

                    if ANNOTATION_AUTO:
                        if "eng" in FILE.split("\\")[-1]:
                            translated_paragraph = paragraph_text
                        else:
                            translated_paragraph = split_and_translate(paragraph_text, "en")

                        LLM_entities = get_LLM_entities(translated_paragraph)
                        extract_LLM(LLM_entities, annotation_data, f"{parent_uri}/text/{paragraph_id}")

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
        tag_div_type = tag_div["type"].title().replace(" ", "") if (
                ("textpart" not in tag_div["type"]) and not any(c.isnumeric() for c in tag_div["type"])
        ) else tag_div["subtype"].title().replace(" ", "")

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


def extraction_data(FILE,CSV):
    with (open(FILE, 'r', encoding="UTF-8") as xml_file):

        xml_parser = bs(xml_file, "lxml-xml")
        oeuvre_id, oeuvre_title, author, date, editor = extract_sourcedesc_data(xml_parser)
        body_parser = xml_parser.body

        link_data = []
        link_labels = ["parent_uri", "type", "id", "title", "child"]
        paragraph_data = []
        paragraph_labels = ["parent_uri", "type", "id", "title", "text", "author", "work"]
        metadata_labels = ["uri", "id", "type", "title", "author", "date", "editor", "prov"]
        annotation_data = []
        annotation_labels = ["paragraph_uri", "concept_uri", "mention", "score", "origin"]

        text_tag = xml_parser.find("text")
        lang_suffix = text_tag.get("xml:lang", "") if text_tag else ""
        uri = f"http://ns.inria.fr/zoomathia/{clean_uri(author).replace(' ', '_')}/{oeuvre_id}/{lang_suffix}"

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
    g = load(g, "../th310.ttl")

    thesaurus_dict = get_all_thesaurus_concepts(g)

    directory_path = ('../texts/')
    xml_files = find_xml_files(directory_path)
    for xml_file in xml_files[10:]:

        print(xml_file)
        FILE = xml_file
        CSV = ".".join(FILE.split("\\")[-1].split(".")[0:-1])
        extraction_data(FILE, CSV)

    print("End of CSV generation")
