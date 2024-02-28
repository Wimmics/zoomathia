import os
from bs4 import BeautifulSoup as bs
from deep_translator import GoogleTranslator
from tqdm import tqdm


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


def translate_text_using_deep_translator(bs_content, balises):
    print(balises)
    for balise in balises:
        for element in tqdm(bs_content.find_all(balise)):
            # print(element)
            original_text = element.text
            # print(original_text)
            if original_text:
                translated_text_en = split_and_translate(original_text, "en")  # translator.translate(original_text)
                #print(translated_text_en)
                translated_text_it = split_and_translate(original_text,
                                                         "it")  # translate_large_text(original_text, translator_it)
                # create new element for english translation
                translated_element_en = bs_content.new_tag(balise)
                translated_element_en["lang"] = "en"
                translated_element_en.string = translated_text_en

                # create new element for italian translation
                translated_element_it = bs_content.new_tag(balise)
                translated_element_it["lang"] = "it"
                translated_element_it.string = translated_text_it
                # insert elements into xml
                element.insert_after(translated_element_en)
                element.insert_after(translated_element_it)


    return bs_content


def write_xml_with_translation(bs_content, file, target_directory):
    # Use the prettify() method to obtain the prettified XML content
    prettified_xml = bs_content.prettify()
    # Remove the <html> and <body> tags
    prettified_xml = prettified_xml.replace('<html>', '').replace('</html>', '').replace('<body>', '').replace(
        '</body>', '')

    # Write the updated XML to a new file
    file_name, file_extension = os.path.splitext(os.path.basename(file.name))
    file_path = os.path.join(target_directory, file_name + "_translated.xml")

    with open(file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(prettified_xml)
    print("file written")


def main_translation(files, directory_path, translated_data_path):
    for file_name in files:
        file_path = os.path.join(directory_path, file_name)
        element_to_translate = []

        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='UTF-8') as file:
                # Read the XML file
                content = file.read()
                bs_content = bs(content, "xml")
                if bs_content.find_all("p"):
                    element_to_translate.append("p")
                if bs_content.find_all("l"):
                #    print("I m here")
                    element_to_translate.append("l")
                  #  print(element_to_translate)
                #if bs_content.find_all(['p', 'l']):
                   # element_to_translate=element
                   # print(element_to_translate)
                    # Translate the text content of the element
                    #original_text = element.get_text(strip=True)

                # Translate data

                bs_content_translated = translate_text_using_deep_translator(bs_content, element_to_translate)
                write_xml_with_translation(bs_content_translated, file, translated_data_path)
