from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os
import glob
from tqdm import tqdm
from deep_translator import GoogleTranslator
from urllib.error import HTTPError

import spacy

API_ENDPOINT_URL = "http://nerd.huma-num.fr/nerd/service"

nlp_model = spacy.load("en_core_web_sm")

SUPPORTED_DIV = ["poem", "book", "chapter", "section", "edition"]
DEBUG = False

def split_and_translate(text, lang_target, max_chunk_length=1000):
    chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
    #print(chunks)
    translated_chunks = []

    for chunk in chunks:
        translated_chunk = GoogleTranslator(source='auto', target=lang_target).translate(chunk)
        if translated_chunk is not None:
            translated_chunks.append(translated_chunk)

    translated_text = ' '.join(translated_chunks)
    return translated_text


def get_NER_from_dbpedia(element,lg="en"):

    if "entityfishing" in list(map(lambda x: x[0], nlp_model.pipeline)):
        nlp_model.remove_pipe("entityfishing")
    if not "dbpedia_spotlight" in list(map(lambda x: x[0], nlp_model.pipeline)):
        nlp_model.add_pipe('dbpedia_spotlight', config={'dbpedia_rest_endpoint': 'http://localhost:2222/rest', 'confidence': 0.6})
    try:
        en_text = nlp_model(element)
    except Exception as err:
        print(err)
        print(element)
        print(FILE)
        return []

    #print("dbpedia", en_text.ents)
    return en_text.ents

def get_NER_from_wikidata(element, lg="en"):

    if "dbpedia_spotlight" in list(map(lambda x: x[0], nlp_model.pipeline)):
        nlp_model.remove_pipe("dbpedia_spotlight")
    if not "entityfishing" in list(map(lambda x: x[0], nlp_model.pipeline)):
        nlp_model.add_pipe("entityfishing", config={"language": "en", "api_ef_base": API_ENDPOINT_URL})

    en_text = nlp_model(element)
    #print("wikidata", en_text.ents)
    return en_text.ents


def extract_dbpedia(entities, annotations, paragraph):
    Dbpedia_category_list_to_filter = ["DBpedia:MusicalWork", "DBpedia:MusicalArtist",
                                       "Schema:MusicGroup",
                                       "Schema:MusicAlbum", "Schema:MusicRecording", "DBpedia:Film",
                                       "DBpedia:MusicGenre", "Memory_management",
                                       "DBpedia:Device", "DBpedia:InformationAppliance",
                                       "Schema:CreativeWork", "DBpedia:TelevisionShow",
                                       "DBpedia:Software", "DBpedia:VideoGame",
                                       "DBpedia:Magazine", "DBpedia:BroadcastNetwork",
                                       "DBpedia:Company"]
    link_dbpedia_to_filter = ["film", "music", "song"]

    for ent in entities:
        if ent.kb_id_ == None or ent.kb_id_ == '':
            continue
        if (ent.kb_id_ is not None) and not (any([x in ent.kb_id_ for x in link_dbpedia_to_filter])):
            annotations.append([paragraph,
                                ent.kb_id_,
                                ent.text,
                                #ent._.dbpedia_raw_result['@similarityScore'],
                                0.6,
                                "DBpedia"])


def extract_wikidata(entities, annotations, paragraph):
    for ent in entities:
        if ent._.url_wikidata is None or ent._.url_wikidata == '':
            continue
        if ent._.nerd_score is not None and ent._.nerd_score >= 0.6:
            #print("label", ent.label_)
            annotations.append([paragraph,
                                ent._.url_wikidata,
                                ent.text,
                                ent._.nerd_score,
                                "wikidata"])


def extract_sourcedesc_data(source):
    """
        Extract metadata from XML-TEI header
        *Those information cannot be found in the body*
    """

    date = strip_text(source.sourceDesc.date.text) if source.sourceDesc.date else strip_text(
        source.titleStmt.date.text) if source.titleStmt.date else strip_text(source.publicationStmt.date.text)
    editor = strip_text(source.titleStmt.editor.text) if source.titleStmt.editor else "Unknown editor"
    author = strip_text(source.titleStmt.author.text) if source.titleStmt.author else strip_text(
        source.sourceDesc.author.text)
    oeuvre_title = strip_text(source.titleStmt.title.text)
    oeuvre_id = strip_text(source.titleStmt.title.text).replace(" ", "_").lower()

    return oeuvre_id, oeuvre_title, author, date, editor


def does_it_have_children_div(node):
    """
        Check if the given node has "div-like" children
        div-like => div1, div2... tags that start with 'div'
    """
    return node.find_all(re.compile('^div'))


def strip_text(txt):
    txt = txt.strip().replace("\r", "").replace("\n", "").replace("\t", "").replace("(","").replace(")","")
    return re.sub(r"\s+", " ", txt)


def strip_paragraph_text(txt):
    txt = txt.strip().replace("\r", "").replace("\n", " ").replace("\t", "").replace("(", "").replace(")", "")
    return re.sub(r"\s+", " ", txt)


def find_xml_files(directory):
    pattern = os.path.join(directory, '**', '*.xml')
    xml_files = glob.glob(pattern, recursive=True)
    return xml_files


def extract_paragraph(parent_division, parent_data, parent_uri, link_data, paragraph_data, annotation_data):

    if len(parent_division.find_all(["p"])) == 0:
        for p_id, p in tqdm(enumerate(parent_division.find_all(["l"], recursive=False), 1)):

            paragraph_id = p_id
            paragraph_text = strip_paragraph_text(p.text)
            translated_paragraph = split_and_translate(paragraph_text, "en")

            wikidata_entities = get_NER_from_wikidata(translated_paragraph)
            extract_wikidata(wikidata_entities, annotation_data, f"{parent_uri}/{paragraph_id}")
            dbpedia_entities = get_NER_from_dbpedia(translated_paragraph)
            extract_dbpedia(dbpedia_entities, annotation_data, f"{parent_uri}/{paragraph_id}")

            if p.head:
                paragraph_title = strip_paragraph_text(p.head.text)
            else:
                paragraph_title = ""
            # ["parent_uri", "type", "id", "title", "child"]
            link_data.append([parent_data[0], parent_data[1], parent_data[2], parent_data[3], f"{parent_uri}/{paragraph_id}"])
            # ["parent_uri", "type", "id", "title", "text"]
            paragraph_data.append([parent_uri, "Paragraph", paragraph_id, paragraph_title, paragraph_text])
    else:
        p_id = 1
        for p in tqdm(parent_division.find_all(["p"])):
            if not p.find_parent('p'):
                # remove useless empty text (maybe error of generation)
                if strip_text(p.text) == "":
                    continue

                if p.head:
                    paragraph_title = strip_paragraph_text(p.head.text)
                else:
                    paragraph_title = ""

                if parent_data[1] == "BekkerPage":
                    paragraph_id = 0 if "a" in parent_data[3] else 1
                    paragraph_text = strip_paragraph_text(p.text)
                    translated_paragraph = split_and_translate(paragraph_text, "en")

                    wikidata_entities = get_NER_from_wikidata(translated_paragraph)
                    extract_wikidata(wikidata_entities, annotation_data, f"{parent_uri}/{paragraph_id}")
                    dbpedia_entities = get_NER_from_dbpedia(translated_paragraph)
                    extract_dbpedia(dbpedia_entities, annotation_data, f"{parent_uri}/{paragraph_id}")

                    # ["parent_uri", "type", "id", "title", "child"]
                    link_data.append([parent_data[0], parent_data[1], parent_data[2], parent_data[2],
                                      f"{parent_uri}/{paragraph_id}"])
                    # ["parent_uri", "type", "id", "title", "text"]
                    paragraph_data.append([parent_uri, "Paragraph", paragraph_id, paragraph_title, paragraph_text])
                else:
                    paragraph_id = p_id
                    paragraph_text = strip_paragraph_text(p.text)
                    translated_paragraph = split_and_translate(paragraph_text, "en")

                    wikidata_entities = get_NER_from_wikidata(translated_paragraph)
                    extract_wikidata(wikidata_entities, annotation_data ,f"{parent_uri}/{paragraph_id}" )
                    dbpedia_entities = get_NER_from_dbpedia(translated_paragraph)
                    extract_dbpedia(dbpedia_entities, annotation_data ,f"{parent_uri}/{paragraph_id}" )

                    # ["parent_uri", "type", "id", "title", "child"]
                    link_data.append([parent_data[0], parent_data[1], parent_data[2], parent_data[3], f"{parent_uri}/{paragraph_id}"])
                    # ["parent_uri", "type", "id", "title", "text"]
                    paragraph_data.append([parent_uri, "Paragraph", paragraph_id, paragraph_title, paragraph_text])
                    p_id += 1
    try:
        return paragraph_id, paragraph_text
    except UnboundLocalError:
        print("Paragraph_id and paragraph_text is not defined")
        print(parent_uri)
        print(parent_division)
        exit(0)

def extraction_data(FILE,CSV):
    with (open(FILE, 'r', encoding="UTF-8") as xml_file):
        xml_parser = bs(xml_file, "lxml-xml")
        oeuvre_id, oeuvre_title, author, date, editor = extract_sourcedesc_data(xml_parser)
        body_parser = xml_parser.body
        link_data = []
        link_labels = ["parent_uri", "type", "id", "title", "child"]
        paragraph_data = []
        paragraph_labels = ["parent_uri", "type", "id", "title", "text"]
        uri = f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}"
        metadata = [[uri, oeuvre_id, "Oeuvre", oeuvre_title, author, date, editor, FILE]]
        metadata_labels = ["uri", "id", "type", "title", "author", "date", "editor", "prov"]
        annotation_data = []
        annotation_labels = ["paragraph_uri", "concept_uri", "mention", "score","origin"]


        # Edition type case is unknown to implement
        for first_id, first_div in tqdm(enumerate(body_parser.find_all(re.compile("^div"), recursive=False), 1)):
            first_div_type = first_div["type"].title().replace(" ", "") if first_div["type"] != "textpart" else first_div["subtype"].title().replace(" ", "")
            first_div_id = first_id
            if first_div.has_attr("n"):
                first_div_title = first_div["n"]
            elif first_div.head:
                first_div_title = strip_text(first_div.head.text)
            else:
                first_div_title = first_id

            # Case for bekker page
            if first_div_type == "BekkerPage":
                #extract number from the title
                first_div_id = int(re.search(r"\d+", first_div_title).group())

            current_uri = f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}/{first_div_id}"
            link_data.append([uri, "Oeuvre", oeuvre_id, oeuvre_title, current_uri])

            # First division has direct paragraph as children
            if not does_it_have_children_div(first_div):
                extract_paragraph(first_div,
                                  [f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}",
                                   first_div_type, first_div_id, first_div_title],
                                  current_uri, link_data, paragraph_data, annotation_data)
            else:
                for second_id, second_div in enumerate(first_div.find_all(re.compile("^div"), recursive=False), 1):
                    second_div_type = second_div["type"].title().replace(" ", "")  if second_div["type"] != "textpart" else second_div["subtype"].title().replace(" ", "")
                    second_div_id = second_id
                    if second_div.head:
                        second_div_title = strip_text(second_div.head.text)
                    else:
                        second_div_title = second_div["n"]

                    current_uri = f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}/{first_div_id}/{second_div_id}"
                    link_data.append(
                        [f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}",
                                     first_div_type, first_div_id, first_div_title, current_uri])

                    if not does_it_have_children_div(second_div):
                        extract_paragraph(second_div, [
                            f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}/{first_div_id}",
                                   second_div_type, second_div_id, second_div_title],
                                          current_uri, link_data, paragraph_data, annotation_data)
                    else:
                        for third_id, third_div in enumerate(second_div.find_all(re.compile("^div"), recursive=False), 1):
                            third_div_type = third_div["type"].title().replace(" ", "")  if third_div["type"] != "textpart" else third_div["subtype"].title().replace(" ", "")
                            third_div_id = third_id
                            if third_div.head:
                                third_div_title = strip_text(third_div.head.text)
                            else:
                                third_div_title = third_div["n"]
                            current_uri = f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}/{first_div_id}/{second_div_id}/{third_div_id}"
                            link_data.append(
                                [f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}/{first_div_id}",
                                 second_div_type, second_div_id, second_div_title, current_uri])

                            if not does_it_have_children_div(third_div):
                                extract_paragraph(third_div, [
                                    f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}/{first_div_id}/{second_div_id}",
                                    third_div_type, third_div_id, third_div_title],
                                                  current_uri, link_data, paragraph_data, annotation_data)
                            else:
                                for fourth_id, fourth_div in enumerate(third_div.find_all(re.compile("^div"), recursive=False), 1):
                                    fourth_div_id = fourth_id
                                    fourth_div_type = fourth_div["type"].title().replace(" ", "")  if fourth_div["type"] != "textpart" else third_div["subtype"].title().replace(" ", "")
                                    if fourth_div.head:
                                        fourth_div_title = strip_text(fourth_div.head.text)
                                    else:
                                        fourth_div_title = fourth_div["n"]
                                    current_uri = f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}/{first_div_id}/{second_div_id}/{third_div_id}/{fourth_div_id}"
                                    link_data.append(
                                        [
                                            f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}/{first_div_id}/{second_div_id}",
                                            third_div_type, third_div_id, third_div_title, current_uri])
                                    extract_paragraph(fourth_div, [
                                        f"http://ns.inria.fr/zoomathia/{strip_text(author).replace(' ', '_')}/{oeuvre_id}/{first_div_id}/{second_div_id}/{third_div_id}",
                                        fourth_div_type, fourth_div_id, fourth_div_title],
                                        current_uri, link_data, paragraph_data, annotation_data)

        pd.DataFrame(link_data, columns=link_labels).to_csv('./output/'+CSV+"_link.csv", index=False, encoding='UTF-8')
        pd.DataFrame(paragraph_data, columns=paragraph_labels).to_csv('./output/'+CSV+"_paragraph.csv", index=False, encoding='UTF-8')
        pd.DataFrame(metadata, columns=metadata_labels).to_csv('./output/'+CSV + "_metadata.csv", index=False,
                                                                      encoding='UTF-8')
        pd.DataFrame(annotation_data, columns=annotation_labels).to_csv('./output/'+CSV+"_annotations.csv", index=False)


if __name__ == "__main__":
    directory_path = './'
    xml_files = find_xml_files(directory_path)
    for xml_file in xml_files:
        print(xml_file)
        FILE = xml_file
        CSV = ".".join(FILE.split("\\")[-1].split(".")[0:-1])
        ANNOTATIONS = ".".join(FILE.split("\\")[-1].split(".")[0:-1]) + "_annotated.csv"
        #extraction_step(FILE, CSV, ANNOTATIONS)
        extraction_data(FILE, CSV)
    print("End of CSV generation")
