from bs4 import BeautifulSoup as bs
import pandas as pd
import glob
import os

def find_xml_files(directory):
    pattern = os.path.join(directory, '**', '*.xml')
    xml_files = glob.glob(pattern, recursive=True)
    return xml_files

if __name__ == "__main__" :
    directory_path = './'
    xml_files = find_xml_files(directory_path)
    subtype = []
    type_div = []

    for file in xml_files:
        print(file)
        with open(file, 'r', encoding='utf-8') as f:
            xml_parser = bs(f, "lxml-xml")
            body = xml_parser.body
            for div in body.find_all("div", recursive=False):
                print(div.find_all("quote", recursive=False))
                subtype.append(div.get("subtype"))
                type_div.append(div["type"])
        print()

    type_div = list(set(type_div))
    type_div.sort()

    print(type_div, list(set(subtype)))