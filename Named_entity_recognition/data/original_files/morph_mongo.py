from time import sleep

import pandas as pd
from pymongo import MongoClient
import os
import glob

import ujson as json
import atexit
import subprocess
from py4j.java_gateway import JavaGateway


# Start java gateway
java_process = subprocess.Popen(
    ['java', '-jar', '-Dfile.encoding=UTF-8', 'corese-library-python-4.4.1.jar'])
sleep(1)
gateway = JavaGateway()




# Stop java gateway at the enf od script
def exit_handler():
    gateway.shutdown()
    print('\n' * 2)
    print('Gateway Server Stop!')

atexit.register(exit_handler)
# Import of class
Graph = gateway.jvm.fr.inria.corese.core.Graph
Load = gateway.jvm.fr.inria.corese.core.load.Load
Transformer = gateway.jvm.fr.inria.corese.core.transform.Transformer
QueryProcess = gateway.jvm.fr.inria.corese.core.query.QueryProcess
RDF = gateway.jvm.fr.inria.corese.core.logic.RDF
RESULTFORMAT = gateway.jvm.fr.inria.corese.core.print.ResultFormat
coreseFormat = gateway.jvm.fr.inria.corese.sparql.api.ResultFormatDef

def sparqlQuery(graph, query):
    """Run a query on a graph

    :param graph: the graph on which the query is executed
    :param query: query to run
    :returns: query result
    """
    exec = QueryProcess.create(graph)
    return exec.query(query)


def convert_sparql_to_json(mapping_object):
    """
    Transform sparql Java object map into standard JSON response
    :param mapping_object:
    :return:
    """
    sparql_formater = RESULTFORMAT.create(mapping_object)
    sparql_formater.setSelectFormat(coreseFormat.JSON_FORMAT)

    # Convert string to JSON
    json_convert = json.loads(sparql_formater.toString())
    return json_convert


def load(graph ,path):
    """Load a graph from a local file or a URL

    :param path: local path or a URL
    :returns: the graph load
    """

    ld = Load.create(graph)
    ld.parse(path)

    return graph

def dbpediaClassFiltered(uri, filtered_already_found):
    if uri in filtered_already_found.keys():
        return filtered_already_found[uri]

    q = f"""select * where {{
	service <https://dbpedia.org/sparql> {{
		<{uri}> a ?type
	}}
}}"""
    try:
        result = convert_sparql_to_json(sparqlQuery(g, q))

        for elt in result["results"]["bindings"]:
            if elt["type"]["value"] in filtered_class_list:
                filtered_already_found[uri] = False
                return False
        filtered_already_found[uri] = False
        return True
    except:
        print("Nothing extracted")

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
            FILTER(lang(?label) = "en" || lang(?label) = "fr").
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
    """
    Load data from csv to a mongoDB collection
    :param csv_file:
    :param db_name:
    :param collection_name:
    :param mongo_uri:
    :return:
    """
    # Connexion à MongoDB
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
        # Conversion du DataFrame en dictionnaires et insertion dans MongoDB
        new_columns = list(df.columns)
        new_columns.append("label")

        for row in df.index:
            paragraph_uri = df["paragraph_uri"][row]
            concept_uri = df["concept_uri"][row]
            mention = df["mention"][row]
            score = df["score"][row]
            origin = df["origin"][row]

            if origin == "wikidata" or dbpediaClassFiltered(concept_uri, filtered_already_found):
                data.append([paragraph_uri, concept_uri, mention, score, origin, mention])

            label = concept_uri.split("/")[-1].replace("_", " ") if "dbpedia" in concept_uri else mention
            setQuery(label, data, [paragraph_uri, concept_uri, mention, score, origin])

        df = pd.DataFrame(data, columns=new_columns)

    collection.insert_many(df.to_dict('records'))
    print(f"Chargé {csv_file} dans la collection {collection_name} de la base de données {db_name}")


def clear_mongo_collection(db_name, collection_name, mongo_uri="mongodb://localhost:27017/"):
    """
    Clear old data from the given mongoDB collection
    :param db_name:
    :param collection_name:
    :param mongo_uri:
    :return:
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    clear_result = collection.delete_many({})


if __name__ == "__main__":
    # TODO: script qui execute des conversions morph_xr2rml
    g = Graph()
    g = load(g, "th310.ttl")
    g = load(g, "zoomathia.ttl")

    filtered_already_found = dict()
    zoomathia_linked = dict()
    class_association = dict()

    with open("filter_class.json", "r") as filter_file:
        filtered_class_list = json.load(filter_file)["class"]

    db_name = "Ner"
    csv_files = glob.glob("./output/*.csv")
    #clear_mongo_collection(db_name, "Annotation")
    clear_mongo_collection(db_name, "Paragraph")
    clear_mongo_collection(db_name, "Link")
    clear_mongo_collection(db_name, "Metadata")

    for csv in csv_files:
        print(csv)
        if "link" in csv:
            load_csv_to_mongodb(csv, db_name, "Link")
        elif "paragraph" in csv:
            load_csv_to_mongodb(csv, db_name, "Paragraph")
        elif "annotations" in csv:
            pass
            #load_csv_to_mongodb(csv, db_name, "Annotation")
        else:
            load_csv_to_mongodb(csv, db_name, "Metadata")

