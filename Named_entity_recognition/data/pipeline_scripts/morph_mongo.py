from time import sleep
import time
import re
import sys
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
sleep(6)
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
MAX_TRIES = 50

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
    tentatives = 0
    
    for i in range (MAX_TRIES):
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
            tentatives += 1
            attente = min(5 * tentatives, 60)
            print(f"[{uri}] Echec connexion (Tentative {tentatives}). Reessai dans {attente}s...")
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

        seen_annotations = set()

        for row in df.index:
            paragraph_uri = df["paragraph_uri"][row]
            concept_uri = df["concept_uri"][row]

            if (paragraph_uri, concept_uri) in seen_annotations:
                continue
            seen_annotations.add((paragraph_uri, concept_uri))

            mention = df["mention"][row]
            score = df["score"][row]
            origin = df["origin"][row]

            if origin == "zoomathia_match":
                data.append([paragraph_uri, concept_uri, mention, score, origin, mention])

            else:
                if origin == "wikidata" or dbpediaClassFiltered(concept_uri, filtered_already_found):
                    data.append([paragraph_uri, concept_uri, mention, score, origin, mention])

                label = concept_uri.split("/")[-1].replace("_", " ") if "dbpedia" in concept_uri else mention
                if origin != "zoomathia_match":
                    setQuery(label, data, [paragraph_uri, concept_uri, mention, score, origin])

        df = pd.DataFrame(data, columns=new_columns)

        df = df.drop_duplicates(subset=['paragraph_uri', 'concept_uri'], keep='first')

    records = df.to_dict('records')
    if not records:
        print(f"Ignore (vide) {csv_file} pour la collection {collection_name}")
        return
    collection.insert_many(records)
    print(f"Chargé {csv_file} dans la collection {collection_name} de la base de données {db_name}")


def clear_work_data(work_uri, db_name, mongo_uri="mongodb://localhost:27017/"):
    """Supprime les anciennes donnees d'une oeuvre (avant rechargement suite a une modification)."""
    client = MongoClient(mongo_uri)
    db = client[db_name]
    pattern = re.compile("^" + re.escape(work_uri))

    db["Metadata"].delete_many({"uri": work_uri})
    db["Paragraph"].delete_many({"parent_uri": pattern})
    db["Link"].delete_many({"parent_uri": pattern})
    db["Annotation"].delete_many({"paragraph_uri": pattern})


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
    only_prefixes = None
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            only_prefixes = set(line.strip() for line in f if line.strip())

    g = Graph()
    g = load(g, "th310.ttl")
    g = load(g, "zoomathia.ttl")

    filtered_already_found = load_cache()
    zoomathia_linked = dict()
    class_association = dict()

    with open("filter_class.json", "r") as filter_file:
        filtered_class_list = json.load(filter_file)["class"]

    csv_files = glob.glob("./output/zoo*_*.csv")

    db_name = "Ner"

    MARKER_DIR = "./mongo_loaded"
    os.makedirs(MARKER_DIR, exist_ok=True)

    if not os.listdir(MARKER_DIR):
        # Premier chargement: on part d'une base vide
        clear_mongo_collection(db_name, "Annotation")
        clear_mongo_collection(db_name, "Paragraph")
        clear_mongo_collection(db_name, "Link")
        clear_mongo_collection(db_name, "Metadata")

    # Regroupe les 4 CSV (metadata/link/paragraph/annotations) par oeuvre
    works = {}
    suffixes = {
        "_link.csv": "Link",
        "_paragraph.csv": "Paragraph",
        "_annotations.csv": "Annotation",
        "_metadata.csv": "Metadata",
    }
    for csv in csv_files:
        for suffix, collection_name in suffixes.items():
            if csv.endswith(suffix):
                prefix = os.path.basename(csv)[:-len(suffix)]
                works.setdefault(prefix, {})[collection_name] = csv
                break

    if only_prefixes is not None:
        works = {prefix: files for prefix, files in works.items() if prefix in only_prefixes}

    skipped = 0
    for prefix, files in works.items():
        marker = os.path.join(MARKER_DIR, prefix + ".done")
        latest_csv_mtime = max(os.path.getmtime(csv) for csv in files.values())

        already_loaded = os.path.exists(marker)
        if already_loaded and os.path.getmtime(marker) >= latest_csv_mtime:
            skipped += 1
            continue

        if already_loaded and "Metadata" in files:
            meta_df = pd.read_csv(files["Metadata"])
            if not meta_df.empty:
                # L'URI peut avoir change depuis le dernier chargement (ex: titre corrige).
                # On retrouve l'ancienne URI stockee en base via 'prov' (chemin source),
                # qui lui ne change pas, pour purger les bonnes anciennes donnees.
                prov = meta_df.iloc[0]["prov"]
                client_tmp = MongoClient("mongodb://localhost:27017/")
                old_doc = client_tmp[db_name]["Metadata"].find_one({"prov": prov})
                print(f"Fichier modifie detecte, purge des anciennes donnees pour: {prefix}")
                if old_doc:
                    clear_work_data(old_doc["uri"], db_name)
                clear_work_data(meta_df.iloc[0]["uri"], db_name)

        for collection_name, csv in files.items():
            print(csv)
            print(f"{collection_name} loading on mongodb ...")
            load_csv_to_mongodb(csv, db_name, collection_name)

        with open(marker, "w") as f:
            f.write("done")

    print(f"Oeuvres deja chargees (ignorees): {skipped} / {len(works)}")