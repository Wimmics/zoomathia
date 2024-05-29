# Specify the directory path
import os
from bs4 import BeautifulSoup as bs
import spacy

from tqdm import tqdm
import time

from Named_entity_recognition.annotation_dbpedia import get_NER_from_dbpedia
#from Named_entity_recognition.annotation_wikidata import get_NER_from_wikidata


def annotate_texts(directory_path, target_path):
    lang_use_for_extraction = ["en", "it"]
    element_to_extract = []
    for subdir, _, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(subdir, file_name)

            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    print(file_name)
                    # Read the XML file
                    content = file.read()
                    bs_content = bs(content, "lxml-xml")
                    if bs_content.find_all("p"):
                        element_to_extract.append("p")
                    if bs_content.find_all("l"):
                        element_to_extract.append("l")
                # Number of requests
                # total_requests = 100
                # Number of requests before introducing a delay
                requests_per_delay = 1000

                # Delay in seconds0
                delay_duration = 60 * 0  # 1 minute
                i = 0
                for lg in lang_use_for_extraction:
                    # print(lg)
                    for element in tqdm((bs_content.find_all(element_to_extract, {"lang": lg}))):
                        i = i + 1
                        # for element in bs_content.find_all(element_to_extract, {"lang": lg}):
                        # Check if it's time to introduce a delay
                        if (i) % requests_per_delay == 0:  # and i != total_requests:
                            print(f"Pausing for {delay_duration} seconds...")
                            time.sleep(delay_duration)
                        # else:
                        #english_NER = get_NER_from_wikidata(element, lg)
                        english_DBpedia_NER = get_NER_from_dbpedia(element, lg)

                        #for ent in english_NER.ents:
                           # if ent._.nerd_score is not None and ent._.nerd_score >= 0.6:
                              #  translated_element_en = bs_content.new_tag("note")
                               # translated_element_en["type"] = "automatic"
                                #translated_element_en["source"] = "Wikidata"
                             #   translated_element_en[ent.label_] = ent.text
                               # translated_element_en["mention"] = ent.text
                                #translated_element_en["category"] = ent.label_
                                #translated_element_en["start"] = ent.start_char
                                #translated_element_en["end"] = ent.end_char
                                #translated_element_en["lang"] = lg
                                #translated_element_en["score"] = ent._.nerd_score
                                #if ent._.url_wikidata is not None:
                                 #   translated_element_en["link"] = ent._.url_wikidata
                                #element.append(translated_element_en)

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

                        for ent in english_DBpedia_NER.ents:
                            if (ent._.dbpedia_raw_result['@types'] is not None and not (
                                    any([x in ent._.dbpedia_raw_result['@types'] for x in
                                         Dbpedia_category_list_to_filter]))):
                                if ((ent.kb_id_ is not None) and not (
                                any([x in ent.kb_id_ for x in link_dbpedia_to_filter]))):
                                    translated_element_en = bs_content.new_tag("note")
                                    translated_element_en["type"] = "automatic"
                                    translated_element_en["source"] = "DBpedia"
                                   # translated_element_en[ent.label_] = ent.text
                                    translated_element_en["mention"] = ent.text
                                    surface_form = ent._.dbpedia_raw_result['@offset']
                                    offset = int(ent._.dbpedia_raw_result['@offset'])
                                    translated_element_en["start"] = offset
                                    translated_element_en["end"] = offset + len(surface_form)
                                    translated_element_en["lang"] = lg
                                    translated_element_en["score"] = ent._.dbpedia_raw_result['@similarityScore']
                                    translated_element_en["category"] = ent._.dbpedia_raw_result['@types']
                                    if ent.kb_id_ is not None:
                                        translated_element_en["link"] = ent.kb_id_
                                    element.append(translated_element_en)

                # Use the prettify() method to obtain the prettified XML content
                prettified_xml = bs_content.prettify()
                # Remove the <html> and <body> tags
               # prettified_xml = prettified_xml.replace('<html>', '').replace('</html>', '').replace('<body>',
                #                                                                                     '').replace(
                 #   '</body>', '')
                # checking if the directory demo_folder
                # exist or not.
                file_name, file_extension = os.path.splitext(os.path.basename(file.name))

                file_path = os.path.join(target_path, file_name + "_extracted.xml")
                print(file_name)
                print(file_path)
                with open(file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(str(prettified_xml))
                print("file written")

