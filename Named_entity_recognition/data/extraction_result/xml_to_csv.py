from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os
import glob

SUPPORTED_DIV = ["poem", "book", "chapter", "section", "edition"]
DEBUG = False


def extract_sourcedesc_data(source):
    """
        Extract metadata from XML-TEI header
        *Those information cannot be found in the body*
    """

    date = strip_text(source.sourcedesc.date.text) if source.sourcedesc.date else strip_text(source.titlestmt.date.text) if source.titlestmt.date else strip_text(source.publicationstmt.date.text)
    # publisher = f"{source.sourcedesc.publisher.text} - {source.sourcedesc.pubPlace.text}"
    editor = strip_text(source.sourcedesc.editor.text) if source.sourcedesc.editor else strip_text(source.titlestmt.editor.text) if source.titlestmt.editor else "Unknown editor"
    author = strip_text(source.sourcedesc.author.text) if source.sourcedesc.author else strip_text(source.titlestmt.author.text)
    oeuvre_title = strip_text(source.sourcedesc.title.text)
    oeuvre_id = strip_text(source.sourcedesc.title.text).replace(" ", "_").lower()

    if DEBUG:
        print(f"Title: {oeuvre_title}\t id: {oeuvre_id}")
        print(f"Author: {author}\t date: {date}\t editor: {editor}")

    return oeuvre_id, oeuvre_title, author, date, editor


def get_book_title(xml):
    if not xml.sourcedesc.biblScope:
        book_id = xml.titlestmt.title.text.lower().replace(" ", "_").replace("\n", "").replace("\r", "")
        book_title = xml.titlestmt.title.text.replace("\n", "").replace("\r", "")
    else:
        book_id = strip_text(f"{xml.sourcedesc.biblScope['type']}_{xml.sourcedesc.biblScope.text}").lower().replace(" ", "_")
        book_title = f"{xml.sourcedesc.biblScope['type']} {xml.sourcedesc.biblScope.text}"

    return book_id, book_title


def does_it_have_children_div(node):
    """
        Check if the given node has "div-like" children
        div-like => div1, div2... tags that start with 'div'
    """
    if DEBUG:
        print(f"{node.name} children: {node.find_all(re.compile('^div'))}")

    return node.find_all(re.compile('^div'))


def strip_text(txt):
    txt = txt.strip().replace("\r", "").replace("\n", "").replace("\t", "")
    return re.sub(" +", " ", txt)


def is_titlestmt_book_title(stmt_title, book_title):
    return stmt_title == book_title


def extraction_step(FILE, CSV, ANNOTATIONS):
    labels = ["oeuvre_id", "oeuvre_title", "author", "date", "editor",
              "book_id", "book_title",
              "chapter_id", "chapter_title",
              "paragraph_id", "paragraph_text"]
    with (open(FILE, 'r', encoding="UTF-8") as xml_file):
        xml_parser = bs(xml_file, "lxml-xml")

        data = []
        annotation = []

        oeuvre_id, oeuvre_title, author, date, editor = extract_sourcedesc_data(xml_parser)
        # Title of the current fragment (check if it's different from the source information)
        statement_title = strip_text(xml_parser.titlestmt.title.text)

        body_parser = xml_parser.body
        for first_level in body_parser.find_all(re.compile("^div"), recursive=False):
            if DEBUG:
                print(f"First level div {first_level}")
            # To only work on div tag
            if "div" in first_level.name:
                division_type = first_level['type'] if first_level['type'] not in ["textpart"] else first_level["subtype"]
            else:
                continue

            # What is the first level of div
            # XML body start with book
            if division_type in ['book']:
                # TODO: if there is no head tag to specify a title, what to do ?
                book_title = strip_text(first_level.head.text) if first_level.head else strip_text(f"{statement_title} - {first_level['n']}")
                # TODO: if there is no n attributes to specify a number, what to do ?
                book_id = first_level['n']

                if not does_it_have_children_div(first_level):
                    chapter_title = f"Fragment text of book {book_id}"
                    chapter_id = f"fragment_text_of_book_{book_id}"
                    p_id = 0
                    for p in first_level.find_all("l"):
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

    print(len(data))
    print([len(x) for x in data])
    print(len(labels))
    pd.DataFrame(data, columns=labels).to_csv(CSV, index=False, encoding='UTF-8')
    pd.DataFrame(annotation, columns=["oeuvre_id", "author", "book_id", "chapter_id", "paragraph_id","annotation_id", "mention", "link", "mention_without_space"]).to_csv(ANNOTATIONS, index=False, encoding='UTF-8')

def find_xml_files(directory):
    pattern = os.path.join(directory, '**', '*.xml')
    xml_files = glob.glob(pattern, recursive=True)
    return xml_files


if __name__ == "__main__":
    directory_path = './'
    xml_files = find_xml_files(directory_path)
    for xml_file in xml_files:
        print(xml_file)
        FILE = xml_file
        CSV = "".join(FILE.split("\\")[-1].split(".")[0:-1]) + ".csv"
        ANNOTATIONS = "".join(FILE.split("\\")[-1].split(".")[0:-1]) + "_annotated.csv"
        print(FILE, CSV, ANNOTATIONS)
        extraction_step(FILE, CSV, ANNOTATIONS)
    print("End of CSV generation")
