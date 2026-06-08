from time import sleep
import time
import requests

import pandas as pd
from pymongo import MongoClient
import os
import glob

import ujson as json
import atexit
import subprocess
from py4j.java_gateway import JavaGateway


java_process = subprocess.Popen(
    ['java', '-jar', '-Dfile.encoding=UTF-8', 'corese-library-python-4.4.1.jar'])
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

CACHE_FILE = "dbpedia_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return dict()

def save_cache(cache_dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_dict, f, indent=4)


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


def dbpediaClassFiltered(uri, filtered_already_found):
    if uri in filtered_already_found.keys():
        # print(f"{uri} already in cache and : {filtered_already_found[uri]}")
        return filtered_already_found[uri]

    q = f"""
    SELECT * WHERE {{
        <{uri}> a ?type
    }}
    """
    
    url = "https://dbpedia.org/sparql"
    params = {"query": q, "format": "application/json"}
    tentative = 0
    
    while True:
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status() 
            
            result = response.json()

            if not result or "results" not in result or not result["results"]["bindings"]:
                filtered_already_found[uri] = True
                save_cache(filtered_already_found)
                return True

            for elt in result["results"]["bindings"]:
                if elt["type"]["value"] in filtered_class_list:
                    filtered_already_found[uri] = False
                    # print(f"elt: {elt["type"]["value"]}, uri: {uri} is False")
                    save_cache(filtered_already_found)
                    return False
                blacklist = ["album", "film"]
                for word in blacklist:
                    if word in uri:
                        filtered_already_found[uri] = False
                        save_cache(filtered_already_found)
                        return False
            
            filtered_already_found[uri] = True
            # print(f"elt:{elt["type"]["value"]}, uri: {uri} is True")
            save_cache(filtered_already_found)
            return True

        except requests.exceptions.RequestException as e:
            tentative += 1
            attente = min(5 * tentative, 60)
            print(f"[{uri}] Echec connexion (Tentative {tentative}). Reessai dans {attente}s...")
            time.sleep(attente)


def linkClassToOntology(name, class_link):
    if name in class_link.keys():
        return class_link[name]

    q = f"""select ?class where {{
  ?class a rdfs:Class;
	rdfs:label ?label
  filter(str(?label) = "{name}")
}}"""
    result = convert_sparql_to_json(sparqlQuery(g, q))
    test = []
    for elt in result["results"]["bindings"]:
        class_association[name] = elt["class"]["value"].split("#")[-1]
        test.append(elt["class"]["value"].split("#")[-1])

    if not test:
        class_link[name] = "UnidentifiedPart"
        return "UnidentifiedPart"
    elif len(test) > 1:
        print("More than one classes posssible")
        print(name, test)
        return test[0]
    return test[0]


def setQuery(label, df, previous):
    if label in zoomathia_linked.keys():
        for elt in zoomathia_linked[label]:
            df.append([previous[0], elt, previous[2], previous[3], "zoomathia", label])

        return

    q = f"""prefix skos: <http://www.w3.org/2004/02/skos/core#>  .

        SELECT DISTINCT ?x ?label WHERE {{
            ?x a ?type;
                skos:prefLabel ?label.
            FILTER(lang(?label) = "en").
            filter(str(?label) in (ucase(str("{label}")), lcase(str("{label}")), str("{label}"))).
        }}"""

    result = convert_sparql_to_json(sparqlQuery(g, q))

    if not result["results"]["bindings"]:
        return

    zoomathia_linked[label] = []
    for elt in result["results"]["bindings"]:
        zoomathia_linked[label].append(elt["x"]["value"])
        df.append([previous[0], elt["x"]["value"], previous[2], previous[3], "zoomathia", label])



def load_csv_to_mongodb(csv_file, db_name, collection_name, mongo_uri="mongodb://localhost:27017/"):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    df = pd.read_csv(csv_file)
    df = df.where(pd.notnull(df), "")
    
    if collection_name == "Link":
        data = []
        new_columns = list(df.columns)
        for row in df.index:
            parent_uri = df["parent_uri"][row]
            uri_type = linkClassToOntology(df["type"][row], class_association)
            uri_id = df["id"][row]
            uri_title = df["title"][row]
            uri_child = df["child"][row]

            data.append([parent_uri, uri_type, uri_id, uri_title, uri_child])
        df = pd.DataFrame(data, columns=new_columns)

    elif collection_name == "Annotation":
        data = []
        new_columns = list(df.columns)
        new_columns.append("label")

        for row in df.index:
            paragraph_uri = df["paragraph_uri"][row]
            concept_uri = df["concept_uri"][row]
            mention = df["mention"][row]
            score = df["score"][row]
            origin = df["origin"][row]



            if origin == "zoomathia_match":
                data.append([paragraph_uri, concept_uri, mention, score, origin, mention])

            else:
                if origin == "wikidata" or dbpediaClassFiltered(concept_uri, filtered_already_found) :
                    data.append([paragraph_uri, concept_uri, mention, score, origin, mention])

                label = concept_uri.split("/")[-1].replace("_", " ") if "dbpedia" in concept_uri else mention
                if origin != "zoomathia_match":
                    setQuery(label, data, [paragraph_uri, concept_uri, mention, score, origin])

        df = pd.DataFrame(data, columns=new_columns)

    collection.insert_many(df.to_dict('records'))
    print(f"Chargé {csv_file} dans la collection {collection_name} de la base de données {db_name}")


def clear_mongo_collection(db_name, collection_name, mongo_uri="mongodb://localhost:27017/"):
    client = MongoClient(mongo_uri)
    db = client[db_name]

    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
    else:
        collection = db[collection_name]
        clear_result = collection.delete_many({})
        print(f"collection {collection_name} cleared: {clear_result}")


if __name__ == "__main__":
    g = Graph()
    g = load(g, "th310.ttl")
    g = load(g, "zoomathia.ttl")

    filtered_already_found = load_cache()
    zoomathia_linked = dict()
    class_association = dict()

    with open("filter_class.json", "r") as filter_file:
        filtered_class_list = json.load(filter_file)["class"]

    csv_files = glob.glob("./texts.csv")

    db_name = "Ner"
    clear_mongo_collection(db_name, "Annotation")
    clear_mongo_collection(db_name, "Paragraph")
    clear_mongo_collection(db_name, "Link")
    clear_mongo_collection(db_name, "Metadata")

    for csv in csv_files:
        print(csv)
        if "link" in csv:
            print("link loading on mongodb ...")
            load_csv_to_mongodb(csv, db_name, "Link")
        elif "paragraph" in csv:
            print("Paragraph loading on mongodb ...")
            load_csv_to_mongodb(csv, db_name, "Paragraph")
        elif "annotations" in csv:
            print("Annotation loading on mongodb ...")
            load_csv_to_mongodb(csv, db_name, "Annotation")
        else:
            print("Metadata loading on mongodb ...")
            load_csv_to_mongodb(csv, db_name, "Metadata")