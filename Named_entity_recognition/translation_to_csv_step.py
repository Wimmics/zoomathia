import os
import pandas as pd
from bs4 import BeautifulSoup as bs


def get_matadata(files_extracted, directory_path, final_directory_path):
    latin_list = []
    balise=['p','l']

    for file_name in files_extracted:
        file_path = os.path.join(directory_path, file_name)

        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                # Read the XML file
                data = []
                content = file.read()
                bs_content = bs(content, "lxml")

                for item in bs_content.find_all("tei"):  # ("tei"):
                    title = item.find('title').text
                    author = item.find('author').text
                    if item.find('editor') is not None:
                        if (item.find('editor').text is not None):
                            editor = item.find('editor').text
                    if item.find('sponsor') is not None:
                        if (item.find('sponsor').text is not None):
                            sponsor = item.find('sponsor').text
                    date = item.find('date').text

                div_books = bs_content.find_all('div',type="book")
                # Associer chaque 'div' à une liste de 'p' en fonction de la valeur de l'attribut 'data-attr' et attribuer un index
                italian_div_to_p_mapping = {}
                english_div_to_p_mapping = {}
                latin_div_to_p_mapping = {}
                for div in div_books:
                    div_id = div.get('n')
                    div_id_header = ''.join([str(content) for content in div if isinstance(content, str)])

                   # print("div_id_header: ",div_id_header)
                    div_chapter = bs_content.find_all('div')
                    for div_c in div_chapter:
                        div_id_c = div_c.get('n')
                        div_id_c_header = ''.join([str(content) for content in div_c if isinstance(content, str)])
                        print(div_id_c)
                    #for element in div.find_all(balise,{'lang': "it"}):
                     #   italian_p_elements = div.find_all((element), {'lang': "it"})
                      #  if italian_p_elements:
                       #     italian_div_to_p_mapping[div_id] = [p.text.strip() for p in italian_p_elements]
                   # if div.find_all(('l'), {'lang': "it"}):
                    #    italian_p_elements = div.find_all(('l'), {'lang': "it"})
                     #   if italian_p_elements:
                      #      italian_div_to_p_mapping[div_id] = [p.text.strip() for p in italian_p_elements]

                    #if div.find_all(('p'), {'lang': "it"}):
                        italian_p_elements = div_c.find_all((['p', 'l']), {'lang': "it"})
                        if italian_p_elements:
                               italian_div_to_p_mapping[div_id] = [p.text.strip() for p in italian_p_elements]

                    # 'l', {'lang': "it"}
                   # if italian_p_elements:
                        #italian_div_to_p_mapping[div_id] = [p.text.strip() for p in italian_p_elements]

                        english_p_elements=( div_c.find_all((['p', 'l']), {'lang': "en"}))
                        if english_p_elements:
                            english_div_to_p_mapping[div_id] = [p.text.strip() for p in english_p_elements]

                        latin_p_elements = div_c.find_all((['p', 'l']), {'lang': None})
                        if latin_p_elements:
                            latin_div_to_p_mapping[div_id] = [p.text.strip() for p in latin_p_elements]

                        for (latin_key, latin_value), (italian_key, italian_value), (english_key, english_value) in zip(
                            latin_div_to_p_mapping.items(), italian_div_to_p_mapping.items(),
                            english_div_to_p_mapping.items()):

                            for index, (latin, italian, english) in enumerate(zip(latin_value, italian_value, english_value)):
                                index_text =str(int(float(index + 1))) #str(latin_key) + "." + str(int(float(index + 1)))
                                data.append([str((title).replace("\n", "")).replace(" ", ""),
                                         str((author).replace("\n", "")).replace(" ", ""),
                                         str((editor).replace("\n", "")).replace(" ", ""),
                                         str((date).replace("\n", "")).replace(" ", ""),
                                         str((div_id).replace("\n", "")).replace(" ", ""),
                                         str((div_id_header).replace("\n", "")).replace(" ", ""),

                                         str((div_id_c).replace("\n", "")).replace(" ", ""),
                                         str((div_id_c_header).replace("\n", "")).replace(" ", ""),

                                         str((index_text).replace("\n", "")).replace(" ", ""), latin, italian,
                                         english])  # str((sponsor).replace("\n","")).replace(" ","")
                           # print(data)
                df = pd.DataFrame(data, columns=["work_title", "author", "editor", "date", "bookid","booktitle","key_div","title_chapter","index_paragraph",
                                                 "latin_text", "italian_text", "english_text"])  # "sponsor"
                # Save the DataFrame to a CSV file
                file_name, file_extension = os.path.splitext(os.path.basename(file.name))
                file_path = os.path.join(final_directory_path, file_name + "_metadata.csv")
                print(file_name)
                print(file_path)
                df.to_csv(file_path, index=False)
                print("done")


def get_annotations(files_extracted, extracted_directory_path, final_directory_path, div_type):
    latin_list = []
    for file_name in files_extracted:
        file_path = os.path.join(extracted_directory_path, file_name)

        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                # Read the XML file
                data = []
                data_wikidata = []
                content = file.read()
                bs_content = bs(content, "lxml")
                for item in bs_content.find_all("tei"):
                    title = item.find('title').text
                div_books = bs_content.find_all('div', type="book")
                for div_b in div_books:
                    div_book_id = div_b.get('n')
                    div_elements = div_b.find_all('div', type=div_type)  # e <div> element
                    for div in div_elements:
                        div_id = div.get('n')
                        print(div_id)
                    # latin_p_elements = div.find_all('l', {'lang': None})
                    # for paragraph in latin_p_elements:
                        manual_index = 0
                        print("manual_index: ", manual_index, "for: ", div_id)
                        for index_p, p in enumerate(div.find_all((['p', 'l']))):  # (div.find_all('l'))
                            attributesp = p.attrs

                            if not attributesp:
                                manual_index += 1
                                print(len(attributesp))
                                print(("index: ", index_p + 1, ":pppppp", p.text, "manual_index: ", manual_index))
                                index_text = str(manual_index) #str(div_id) + "." + str(manual_index)
                                print("div, text: ", div_id, index_text)

                            note_elements = p.find_all('note')  # Find all <note> elements within the <p> element
                            if note_elements:
                                for index_note, note in enumerate(note_elements):
                                    # index_note=index_text+"."+str(index_note)
                                    # attributes = note.attrs  # Retrieve the attributes of each <note> element
                                    attributes = list(note.attrs.items())
                                    print (attributes)
                                    attributes_names = list(note.attrs.keys())

                                    if len(attributes) >= 9 and len(attributes) > 2:
                                        attribute, mention = attributes[0]
                                        attribute1, end = attributes[2]
                                        attribute3, annotation_lang = attributes[3]
                                        attribute2, concept = attributes[4]
                                        attribute4, start = attributes[7]
                                        attribute5, score = attributes[5]
                                        attribute6, category = attributes[1]
                                        index_note = index_text + "." + str(index_note) + "_" + annotation_lang
                                        data.append([str(title.replace("\n", "")).replace(" ", ""),div_book_id, div_id, index_text,
                                                     index_note, mention, str(mention.replace(" ", "_")), concept, start,
                                                     end, annotation_lang, score, category])
                                    elif 9 > len(attributes) > 2:
                                        attribute, mention = attributes[0]
                                        attribute1, end = attributes[1]
                                        attribute3, annotation_lang = attributes[2]
                                        attribute2, concept = attributes[3]
                                        attribute4, start = attributes[6]
                                        attribute5, score = attributes[4]
                                        category = [attributes_names[0]]
                                        index_note = index_text + "." + str(index_note) + "_" + annotation_lang
                                        data_wikidata.append(
                                            [str(title.replace("\n", "")).replace(" ", ""), div_book_id, div_id, index_text,
                                             index_note, mention, str(mention.replace(" ", "_")), concept, start, end,
                                             annotation_lang, score, category])
                                        print("data: ", data_wikidata)
                df_annotation_dbpedia = pd.DataFrame(data,
                                                     columns=["title", "div_book_id","div", "index_paragraph", "index_annotation",
                                                              "mention", "mention_without_space", "concept", "start",
                                                              "end", "annotation_lang", "score", "category"])
                df_annotation_wikidata = pd.DataFrame(data_wikidata,
                                                      columns=["title", "div_book_id","div", "index_paragraph", "index_annotation",
                                                               "mention", "mention_without_space", "concept", "start",
                                                               "end", "annotation_lang", "score", "category"])
                frames = [df_annotation_dbpedia, df_annotation_wikidata]
                df_annotation = pd.concat(frames)

                file_name, file_extension = os.path.splitext(os.path.basename(file.name))
                file_path = os.path.join(final_directory_path, file_name + "_annotation.csv")
                print(file_name)
                print(file_path)
                df_annotation.to_csv(file_path, index=False)
                print("done")


def main_transformation_to_csv(files_extracted, extracted_directory_path, final_directory_path, div_type):
    get_matadata(files_extracted, extracted_directory_path, final_directory_path)
    get_annotations(files_extracted, extracted_directory_path, final_directory_path, div_type)
