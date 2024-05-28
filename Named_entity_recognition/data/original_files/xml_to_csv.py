from bs4 import BeautifulSoup as bs
import pandas as pd
import re

SUPPORTED_DIV = ["poem", "book", "chapter", "section", "edition"]
DEBUG = False


def extract_sourceDesc_data(source):
    """
        Extract metadata from XML-TEI header
        *Those information cannot be found in the body*
    """
    date = source.sourceDesc.date.text if source.sourceDesc.date else source.titleStmt.date.text if source.titleStmt.date else source.publicationStmt.date.text
    # publisher = f"{source.sourceDesc.publisher.text} - {source.sourceDesc.pubPlace.text}"
    editor = strip_paragraph_text(source.sourceDesc.editor.text) if source.sourceDesc.editor else strip_paragraph_text(source.titleStmt.editor.text) if source.titleStmt.editor else "Unknown editor"
    author = strip_paragraph_text(source.sourceDesc.author.text) if source.sourceDesc.author else strip_paragraph_text(source.titleStmt.author.text)
    oeuvre_title = strip_paragraph_text(xml_parser.sourceDesc.title.text)
    oeuvre_id = strip_paragraph_text(xml_parser.sourceDesc.title.text).replace(" ","_").lower()

    if DEBUG:
        print(f"Title: {oeuvre_title}\t id: {oeuvre_id}")
        print(f"Author: {author}\t date: {date}\t editor: {editor}")

    return oeuvre_id, oeuvre_title, author, date, editor


def get_book_title(xml):
    if not xml.sourceDesc.biblScope:
        book_id = xml.titleStmt.title.text.lower().replace(" ", "_").replace("\n", "").replace("\r", "")
        book_title = xml.titleStmt.title.text.replace("\n", "").replace("\r", "")
    else:
        book_id = f"{xml.sourceDesc.biblScope['type']}_{xml.sourceDesc.biblScope.text}"
        book_title = f"{xml.sourceDesc.biblScope['type']} {xml.sourceDesc.biblScope.text}"

    return book_id, book_title


def does_it_have_children_div(node):
    """
        Check if the given node has "div-like" children
        div-like => div1, div2... tags that start with 'div'
    """
    if DEBUG:
        print(f"{node.name} children: {node.find_all(re.compile('^div'))}")

    return node.find_all(re.compile('^div'))


def strip_paragraph_text(txt):
    txt = txt.strip().replace("\r", "").replace("\n", "").replace("\t", "")
    return re.sub(" +", " ", txt)


def is_titleStmt_book_title(stmt_title, book_title):
    return stmt_title == book_title


FILE = "tlg0007/tlg132/tlg0007.tlg132.perseus-grc1.xml"
CSV = "tlg132-metadata.csv"

if __name__ == "__main__":
    labels = ["oeuvre_id", "oeuvre_title", "author", "date", "editor",
              "book_id", "book_title",
              "chapter_id", "chapter_title",
              "paragraph_id", "paragraph_text"]
    with (open(FILE, 'r', encoding="UTF-8") as xml_file):
        xml_parser = bs(xml_file, "lxml-xml")
        data = []

        oeuvre_id, oeuvre_title, author, date, editor = extract_sourceDesc_data(xml_parser)
        # Title of the current fragment (check if it's different from the source information)
        statement_title = xml_parser.titleStmt.title.text

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
                book_title = strip_paragraph_text(first_level.head.text) if first_level.head else strip_paragraph_text(f"{statement_title} - {first_level['n']}")
                # TODO: if there is no n attributes to specify a number, what to do ?
                book_id = first_level['n']

                if not does_it_have_children_div(first_level):
                    chapter_title = f"Fragment text of book {book_id}"
                    chapter_id = f"fragment_text_of_book_{book_id}"

                    for p_id, p in enumerate(first_level.find_all("l")):
                        paragraph_id = p_id + 1
                        paragraph_text = strip_paragraph_text(p.text)
                        data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                                 book_id, book_title,
                                                 chapter_id, chapter_title,
                                                 paragraph_id, paragraph_text])
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
                                div_type = third_level["type"]
                                if len(list(third_level.find_all(['p', 'l'], recursive=False))) == 1:
                                    paragraph_id = third_level['n']
                                    paragraph_text = strip_paragraph_text(third_level.p.text)
                                    data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                                 book_id, book_title,
                                                 chapter_id, chapter_title,
                                                 paragraph_id, paragraph_text])

                                else:
                                    for p_id, p in enumerate(third_level.find_all(re.compile(r"p | l"))):
                                        paragraph_id = p_id + 1
                                        paragraph_text = strip_paragraph_text(p.text)
                                        data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                                     book_id, book_title,
                                                     chapter_id, chapter_title,
                                                     paragraph_id, paragraph_text])


                        else:
                            for p_id, p in enumerate(second_level.find_all(["p", "l"], recursive=False)):
                                paragraph_id = p_id + 1
                                paragraph_text = strip_paragraph_text(p.text)
                                data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                             book_id, book_title,
                                             chapter_id, chapter_title,
                                             paragraph_id, paragraph_text])

            # XML body start with chapter
            if division_type == 'chapter':

                book_id, book_title = get_book_title(xml_parser)
                chapter_id = first_level['n'] if first_level.has_attr("n") else strip_paragraph_text(statement_title).lower().replace(" ","_")
                # Children has a head tag: this is the title of div
                if first_level.head:
                    chapter_title = first_level.head.text
                    # Chapter has directly paragraph under it
                    if not does_it_have_children_div(first_level):
                        print(first_level)
                        exit(0)
                    # Probably sections under it
                    else:
                        for second_level in first_level.find_all(re.compile("^div")):
                            print(second_level)
                        exit(0)
                else:

                    if is_titleStmt_book_title(statement_title, book_title):
                        chapter_title = f"{book_title} - {chapter_id if chapter_id != statement_title else ''}"
                    else:
                        chapter_title = f"{statement_title}{f' - Chapter {chapter_id}' if chapter_id != statement_title else ''}"

                    if not does_it_have_children_div(first_level):
                        for key, paragraph in enumerate(first_level.find_all("p")):
                            if DEBUG:
                                print(key + 1, strip_paragraph_text(paragraph.text))

                            paragraph_id = key + 1
                            paragraph_text = strip_paragraph_text(paragraph.text)
                            data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                         book_id, book_title,
                                         chapter_id, chapter_title,
                                         paragraph_id, paragraph_text])
                    # Probably sections under it
                    else:
                        for second_level in first_level.find_all(re.compile("^div")):
                            for key, paragraph in enumerate(second_level.find_all("p")):
                                if DEBUG:
                                    print(key + 1, strip_paragraph_text(paragraph.text))
                                paragraph_id = second_level['n'] if (
                                        second_level.has_attr('n') and len(list(second_level.find_all('p'))) == 1) else key + 1
                                paragraph_text = strip_paragraph_text(paragraph.text)
                                data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                             book_id, book_title,
                                             chapter_id, chapter_title,
                                             paragraph_id, paragraph_text])

            # XML body start with section (should not have div children)
            if division_type == 'section':
                if xml_parser.sourceDesc.biblScope:
                    book_title = strip_paragraph_text(f"{xml_parser.sourceDesc.biblScope['type']} {xml_parser.sourceDesc.biblScope.text}")
                    book_id =  strip_paragraph_text(f"{xml_parser.sourceDesc.biblScope['type']}{xml_parser.sourceDesc.biblScope.text}")
                else:
                    book_id = strip_paragraph_text(statement_title)
                    book_title =strip_paragraph_text(statement_title).replace(" ","_").lower()

                chapter_title = strip_paragraph_text(statement_title)
                chapter_id = strip_paragraph_text(statement_title).replace(" ", "_").lower()
                sub_children_id = first_level['n']
                for key, paragraph in enumerate(first_level.find_all('p')):
                    paragraph_id = first_level['n'] if (
                            first_level.has_attr('n') and len(list(first_level.find_all('p'))) == 1) else key + 1
                    paragraph_text = strip_paragraph_text(paragraph.text)
                    data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                 book_id, book_title,
                                 chapter_id, chapter_title,
                                 paragraph_id, paragraph_text])

            if division_type == 'edition':
                if not does_it_have_children_div(first_level):
                    book_title = statement_title
                    book_id = statement_title.replace(" ", "_")
                    paragraph_list = []
                    i = 0
                    for child in first_level.find_all():
                        if child.name == 'milestone' and child['unit'] == "card":
                            if paragraph_list:
                                i += 1
                                chapter_title = f"Chapter {i}"
                                chapter_id = i
                                for p_id, p in enumerate(paragraph_list):
                                    paragraph_id = p_id + 1
                                    paragraph_text = strip_paragraph_text(p)
                                    data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                 book_id, book_title,
                                 chapter_id, chapter_title,
                                 paragraph_id, paragraph_text])

                                paragraph_list = []
                        else:
                            if child.name == 'l':
                                paragraph_list.append(child.text)

                    i += 1
                    chapter_title = f"Chapter {i}"
                    chapter_id = i
                    for p_id, p in enumerate(paragraph_list):
                        paragraph_id = p_id + 1
                        paragraph_text = strip_paragraph_text(p)
                        data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                     book_id, book_title,
                                     chapter_id, chapter_title,
                                     paragraph_id, paragraph_text])
                else:
                    for second_level in first_level.find_all(re.compile("^div")):
                        if second_level["type"] == "chapter" or second_level["subtype"] == "chapter":
                            book_id = statement_title.replace(" ", "_")
                            book_title = f"{statement_title} - {first_level.head.text}" if first_level.head else statement_title
                        elif second_level["type"] == "book" or second_level["subtype"] == "book":
                            book_id = f"{statement_title}_book{second_level['n']}"
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
                                for p_id, p in enumerate(third_level.find_all("p", recursive=False)):
                                    if not p.text:
                                        continue
                                    paragraph_id = p_id + 1
                                    paragraph_text = strip_paragraph_text(p.text)
                                    data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                                 book_id, book_title,
                                                 chapter_id, chapter_title,
                                                 paragraph_id, paragraph_text])
                        else:
                            if second_level.head:
                                chapter_title = strip_paragraph_text(second_level.head.text)
                                chapter_id = second_level['n']
                            else:
                                chapter_title = f"Chapter {second_level['n']}"
                                chapter_id = second_level['n']
                            for p_id, p in enumerate(second_level.find_all("p", recursive=False)):
                                if not p.text:
                                    continue
                                paragraph_id = p_id + 1
                                paragraph_text = strip_paragraph_text(p.text)
                                data.append([oeuvre_id, oeuvre_title, author, date, editor,
                                             book_id, book_title,
                                             chapter_id, chapter_title,
                                             paragraph_id, paragraph_text])



            # Current type of division is not an expected one: see SUPPORTED_DIV list
            if division_type not in SUPPORTED_DIV:
                print(
                    f"Error in XML-TEI: current type {division_type} is not supported... Check for subtype if it exists.")
                exit(0)

    print(len(data))
    print([len(x) for x in data])
    print(len(labels))
    pd.DataFrame(data, columns=labels).to_csv(CSV, index=False, encoding='UTF-8')
