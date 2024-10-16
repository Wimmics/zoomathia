from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os
import glob
from tqdm import tqdm
from deep_translator import GoogleTranslator

import spacy



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

    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe('dbpedia_spotlight', config={'confidence': 0.6})

    en_text = nlp(element)

    del nlp
    return en_text.ents

API_ENDPOINT_URL = "http://nerd.huma-num.fr/nerd/service"
def get_NER_from_wikidata(element, lg="en"):

    if lg == "it":
        nlp_model = spacy.load("it_core_news_lg")
        nlp_model.add_pipe("entityfishing", config={"language": lg, "api_ef_base": API_ENDPOINT_URL})
    else:
        nlp_model = spacy.load("en_core_web_sm")
        nlp_model.add_pipe("entityfishing", config={'language': lg, "api_ef_base": API_ENDPOINT_URL})

    en_text = nlp_model(element)
    del nlp_model
    return en_text.ents
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


"""
def extraction_step(FILE, CSV, ANNOTATIONS):
    labels = ["oeuvre_id", "oeuvre_title", "author", "date", "editor",
              "book_id", "book_title",
              "chapter_id", "chapter_title",
              "paragraph_id", "paragraph_text"]
    with (open(FILE, 'r', encoding="UTF-8") as xml_file):
        xml_parser = bs(xml_file, "lxml-xml")

        columns_label = [
            "oeuvre_id", "oeuvre_title", "author", "editor", "date", "file_name",
            "first_div_type", "first_div_id", "first_div_title",
            "second_div_type", "second_div_id", "second_div_title",
            "third_div_type", "third_div_id", "second_div_title",
            "paragraph_id", "paragraph_title", "paragraph_text"
        ]
        data = []
        annotation = []

        oeuvre_id, oeuvre_title, author, date, editor = extract_sourcedesc_data(xml_parser)
        body_parser = xml_parser.body
        
        for first_level in body_parser.find_all(re.compile("^div"), recursive=False):
            # To only work on div tag
            if "div" in first_level.name:
                division_type = first_level['type'] if first_level['type'] != "textpart" else first_level["subtype"]
            else:
                print("strange tag", first_level.name)
                continue

            # What is the first level of div
            # XML body start with book
            if division_type in ['book']:
                if first_level.head:
                    first_div_title = strip_text(first_level.head.text)
                else:
                    first_div_title = strip_text(f"{first_level['n']}")
                first_div_id = first_level['n']
                first_div_type = "Book"

                if not does_it_have_children_div(first_level):
                    
                    p_id = 0
                    for p in first_level.find_all("l"):
                        second_div_title = f"Fragment text of book {book_id}"
                        second_div_id = f"fragment_text_of_book_{book_id}"
                        second_div_type = "Paragraph"
                        for note in p.find_all("note", attrs={"type": "marginal"}):
                            note.extract()
                        for key, annote in enumerate(p.find_all("note", attrs={"type": "automatic"})):
                            link = annote["link"]
                            mention = list(annote.attrs.items())[0][1]
                            mention_without_space = list(annote.attrs.items())[0][1].replace(" ", "_")
                            annotation.append(
                                [oeuvre_id, author, book_id, chapter_id, paragraph_id, key + 1, mention, link,
                                 mention_without_space])
                else:
                    for key, second_level in enumerate(first_level.find_all(re.compile("^div"), recursive=False)):
                        if second_level.head:
                            chapter_title = second_level.head.text
                            chapter_id = second_level['n']
                        else:
                            chapter_title = f"Chapter {second_level['n']}" if second_level.has_attr('n') else key + 1
                            chapter_id = second_level['n'] if second_level.has_attr('n') else key + 1

                        if does_it_have_children_div(second_level):

                            for third_level in second_level.find_all(re.compile("^div"), recursive=False):
                                # TODO: Bout de code à vérifier
                                if len(list(third_level.find_all(['p', 'l'], recursive=False))) == 1:
                                    paragraph_id = third_level['n']
                                    paragraph_text = strip_text(third_level.p.text)
                                    data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                                 book_id, book_title,
                                                 chapter_id, chapter_title,
                                                 paragraph_id, paragraph_text])

                                else:
                                    p_id = 0
                                    for p in third_level.find_all(["p","l"]):
                                        for note in p.find_all("note", attrs={"type": "marginal"}):
                                            note.extract()
                                        if not p.has_attr("lang"):
                                            p_id += 1
                                            paragraph_id = p_id
                                            paragraph_text = strip_text(p.text)
                                            data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                                         book_id, book_title,
                                                         chapter_id, chapter_title,
                                                         paragraph_id, paragraph_text])
                                        else:
                                            for key, annote in enumerate(p.find_all("note", attrs={"type": "automatic"})):
                                                link = annote["link"]
                                                mention = list(annote.attrs.items())[0][1]
                                                mention_without_space = list(annote.attrs.items())[0][1].replace(" ",
                                                                                                                 "_")
                                                annotation.append(
                                                    [oeuvre_id, author, book_id, chapter_id, paragraph_id, key + 1,
                                                     mention, link, mention_without_space])


                        else:
                            p_id = 0
                            for p in second_level.find_all(["p", "l"], recursive=False):
                                # Remove All marginal note that shouldn't be display
                                for note in p.find_all("note", attrs={"type": "marginal"}):
                                    note.extract()
                                if not p.has_attr("lang"):
                                    p_id += 1
                                    paragraph_id = p_id
                                    paragraph_text = strip_text(p.text)
                                    data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                                 book_id, book_title,
                                                 chapter_id, chapter_title,
                                                 paragraph_id, paragraph_text])
                                else:
                                    for key, annote in enumerate(p.find_all("note", attrs={"type": "automatic"})):
                                        link = annote["link"]
                                        mention = list(annote.attrs.items())[0][1]
                                        mention_without_space = list(annote.attrs.items())[0][1].replace(" ", "_")
                                        annotation.append(
                                            [oeuvre_id, author, book_id, chapter_id, paragraph_id, key + 1, mention,
                                             link, mention_without_space])

            # XML body start with chapter
            if division_type == 'chapter':

                book_id, book_title = get_book_title(xml_parser)
                chapter_id = first_level['n'] if first_level.has_attr("n") else strip_text(statement_title).lower().replace(" ", "_")
                # Children has a head tag: this is the title of div
                if first_level.head:
                    chapter_title = first_level.head.text
                    # Chapter has directly paragraph under it
                    if not does_it_have_children_div(first_level):
                        print("Error: case not implemented chapter have direct <p> tags")
                        print(first_level)
                        exit(0)
                    # Probably sections under it
                    else:
                        for second_level in first_level.find_all(re.compile("^div")):
                            print("Error: case not implemented chapter has div under him")
                            print(second_level)
                        exit(0)
                else:

                    if is_titlestmt_book_title(statement_title, book_title):
                        chapter_title = f"{book_title} - {chapter_id if chapter_id != statement_title else ''}"
                    else:
                        chapter_title = f"{statement_title}{f' - Chapter {chapter_id}' if chapter_id != statement_title else ''}"

                    if not does_it_have_children_div(first_level):
                        p_id = 0
                        for paragraph in first_level.find_all("p"):
                            # Remove All marginal note that shouldn't be display
                            for note in paragraph.find_all("note", attrs={"type": "marginal"}):
                                note.extract()
                            if not paragraph.has_attr("lang"):
                                p_id += 1
                                paragraph_id = p_id
                                paragraph_text = strip_text(paragraph.text)
                                data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                             book_id, book_title,
                                             chapter_id, chapter_title,
                                             paragraph_id, paragraph_text])
                            else:
                                for k, annote in enumerate(paragraph.find_all("note", attrs={"type": "automatic"})):
                                    link = annote["link"]
                                    mention = list(annote.attrs.items())[0][1]
                                    mention_without_space = list(annote.attrs.items())[0][1].replace(" ", "_")
                                    annotation.append(
                                        [oeuvre_id, author, book_id, chapter_id, paragraph_id, k + 1, mention, link,
                                         mention_without_space])
                    # Probably sections under it
                    else:
                        for second_level in first_level.find_all(re.compile("^div")):
                            p_id = 0
                            for paragraph in second_level.find_all("p"):
                                # Remove All marginal note that shouldn't be display
                                for note in paragraph.find_all("note", attrs={"type": "marginal"}):
                                    note.extract()
                                if not paragraph.has_attr("lang"):
                                    p_id += 1
                                    paragraph_id = second_level['n'] if (
                                            second_level.has_attr('n') and len(list(second_level.find_all('p'))) == 1) else p_id
                                    paragraph_text = strip_text(paragraph.text)
                                    data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                                 book_id, book_title,
                                                 chapter_id, chapter_title,
                                                 paragraph_id, paragraph_text])
                                else:
                                    for k, annote in enumerate(paragraph.find_all("note", attrs={"type": "automatic"})):
                                        link = annote["link"]
                                        mention = list(annote.attrs.items())[0][1]
                                        mention_without_space = list(annote.attrs.items())[0][1].replace(" ", "_")
                                        annotation.append(
                                            [oeuvre_id, author, book_id, chapter_id, paragraph_id, k + 1, mention,
                                             link, mention_without_space])

            # XML body start with section (should not have div children)
            if division_type == 'section':
                if xml_parser.sourcedesc.biblScope:
                    book_title = strip_text(f"{xml_parser.sourcedesc.biblScope['type']} {xml_parser.sourcedesc.biblScope.text}")
                    book_id = strip_text(f"{xml_parser.sourcedesc.biblScope['type']}{xml_parser.sourcedesc.biblScope.text}").lower().replace(" ","_")
                else:
                    book_id = strip_text(statement_title).replace(" ","_").lower()
                    book_title =  strip_text(statement_title).replace(" ", "_").lower()

                chapter_title = strip_text(statement_title)
                chapter_id = strip_text(statement_title).replace(" ", "_").lower()
                sub_children_id = first_level['n']
                p_id = 0
                for paragraph in first_level.find_all('p'):
                    # Remove All marginal note that shouldn't be display
                    for note in paragraph.find_all("note", attrs={"type": "marginal"}):
                        note.extract()
                    if not paragraph.has_attr("lang"):
                        p_id += 1
                        paragraph_id = first_level['n'] if (
                                first_level.has_attr('n') and len(list(first_level.find_all('p'))) == 1) else p_id
                        paragraph_text = strip_text(paragraph.text)
                        data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                     book_id, book_title,
                                     chapter_id, chapter_title,
                                     paragraph_id, paragraph_text])
                    else:
                        for key, annote in enumerate(paragraph.find_all("note", attrs={"type": "automatic"})):
                            link = annote["link"]
                            mention = list(annote.attrs.items())[0][1]
                            mention_without_space = list(annote.attrs.items())[0][1].replace(" ", "_")
                            annotation.append(
                                [oeuvre_id, author, book_id, chapter_id, paragraph_id, key + 1, mention, link,
                                 mention_without_space])

            if division_type == 'edition':
                if not does_it_have_children_div(first_level):
                    book_title = statement_title
                    book_id = statement_title.replace(" ", "_").lower()
                    paragraph_list = []
                    i = 0
                    for child in first_level.find_all():
                        if child.name == 'milestone' and child['unit'] == "card":
                            if paragraph_list:
                                i += 1
                                chapter_title = f"Chapter {i}"
                                chapter_id = i
                                p_id = 0
                                for p in paragraph_list:
                                    # Remove All marginal note that shouldn't be display
                                    for note in p.find_all("note", attrs={"type": "marginal"}):
                                        note.extract()
                                    if not p.has_attr("lang"):
                                        p_id += 1
                                        paragraph_id = p_id
                                        paragraph_text = strip_text(p.text)
                                        data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                     book_id, book_title,
                                     chapter_id, chapter_title,
                                     paragraph_id, paragraph_text])
                                    else:
                                        for key, annote in enumerate(p.find_all("note", attrs={"type": "automatic"})):
                                            link = annote["link"]
                                            mention = list(annote.attrs.items())[0][1]
                                            mention_without_space = list(annote.attrs.items())[0][1].replace(" ", "_")
                                            annotation.append(
                                                [oeuvre_id, author, book_id, chapter_id, paragraph_id, key + 1, mention,
                                                 link, mention_without_space])
                                paragraph_list = []
                        else:
                            if child.name == 'l':
                                paragraph_list.append(child)

                    i += 1
                    chapter_title = f"Chapter {i}"
                    chapter_id = i
                    p_id = 0
                    for p in paragraph_list:
                        # Remove All marginal note that shouldn't be display
                        for note in p.find_all("note", attrs={"type": "marginal"}):
                            note.extract()
                        if not p.has_attr("lang"):
                            p_id += 1
                            paragraph_id = p_id
                            paragraph_text = strip_text(p.text)
                            data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                         book_id, book_title,
                                         chapter_id, chapter_title,
                                         paragraph_id, paragraph_text])
                        else:
                            for key, annote in enumerate(p.find_all("note", attrs={"type": "automatic"})):
                                link = annote["link"]
                                mention = list(annote.attrs.items())[0][1]
                                mention_without_space = list(annote.attrs.items())[0][1].replace(" ", "_")
                                annotation.append(
                                    [oeuvre_id, author, book_id, chapter_id, paragraph_id, key + 1, mention, link,
                                     mention_without_space])
                else:
                    for second_level in first_level.find_all(re.compile("^div")):
                        if second_level["type"] == "chapter" or second_level["subtype"] == "chapter":
                            book_id = strip_text(statement_title).replace(" ", "_").lower()
                            book_title = f"{statement_title} - {first_level.head.text}" if first_level.head else statement_title
                        elif second_level["type"] == "book" or second_level["subtype"] == "book":
                            book_id = strip_text(f"{statement_title}_book{second_level['n']}").replace(" ","_").lower()
                            book_title = f"{statement_title} - book{second_level['n']}"
                        else:
                            book_id = second_level['n']
                            book_title = f"{oeuvre_title} - Book {book_id}"

                        if does_it_have_children_div(second_level):
                            for third_level in second_level.find_all(re.compile("^div")):
                                if third_level.head:
                                    chapter_title = third_level.head.text
                                    chapter_id = third_level['n']
                                else:
                                    chapter_title = f"Chapter {third_level['n']}"
                                    chapter_id = third_level['n']
                                p_id = 0
                                for p in third_level.find_all("p", recursive=False):
                                    if not p.text:
                                        continue
                                    # Remove All marginal note that shouldn't be display
                                    for note in p.find_all("note", attrs={"type": "marginal"}):
                                        note.extract()
                                    if not p.has_attr("lang"):
                                        p_id += 1
                                        paragraph_id = p_id
                                        paragraph_text = strip_text(p.text)
                                        data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                                     book_id, book_title,
                                                     chapter_id, chapter_title,
                                                     paragraph_id, paragraph_text])
                                    else:
                                        for key, annote in enumerate(p.find_all("note", attrs={"type": "automatic"})):
                                            link = annote["link"]
                                            mention = list(annote.attrs.items())[0][1]
                                            mention_without_space = list(annote.attrs.items())[0][1].replace(" ", "_")
                                            annotation.append(
                                                [oeuvre_id, author, book_id, chapter_id, paragraph_id, key + 1, mention,
                                                 link, mention_without_space])

                        else:
                            if second_level.head:
                                chapter_title = strip_text(second_level.head.text)
                                chapter_id = second_level['n']
                            else:
                                chapter_title = f"Chapter {second_level['n']}"
                                chapter_id = second_level['n']
                            p_id = 0
                            for p in second_level.find_all("p", recursive=False):
                                if not p.text:
                                    continue
                                    # Remove All marginal note that shouldn't be display
                                for note in p.find_all("note", attrs={"type": "marginal"}):
                                    note.extract()
                                if not p.has_attr("lang"):
                                    p_id += 1
                                    paragraph_id = p_id
                                    paragraph_text = strip_text(p.text)
                                    data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                                 book_id, book_title,
                                                 chapter_id, chapter_title,
                                                 paragraph_id, paragraph_text])
                                else:
                                    for key, annote in enumerate(p.find_all("note", attrs={"type": "automatic"})):
                                        link = annote["link"]
                                        mention = list(annote.attrs.items())[0][1]
                                        mention_without_space = list(annote.attrs.items())[0][1].replace(" ","_")
                                        annotation.append(
                                            [oeuvre_id, author, book_id, chapter_id, paragraph_id,key+1, mention, link, mention_without_space])

            # Current type of division is not an expected one: see SUPPORTED_DIV list
            if division_type not in SUPPORTED_DIV:
                print(
                    f"Error in XML-TEI: current type {division_type} is not supported... Check for subtype if it exists.")
                return

    pd.DataFrame(data, columns=labels).to_csv(CSV, index=False, encoding='UTF-8')
    pd.DataFrame(annotation, columns=["oeuvre_id", "author", "book_id", "chapter_id", "paragraph_id","annotation_id", "mention", "link", "mention_without_space"]).to_csv(ANNOTATIONS, index=False, encoding='UTF-8')
"""
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
