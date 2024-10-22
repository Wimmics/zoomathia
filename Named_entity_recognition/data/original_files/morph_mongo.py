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

def setQuery(label, df, previous):
    q = f"""prefix skos: <http://www.w3.org/2004/02/skos/core#>  .

        SELECT DISTINCT ?x ?label WHERE {{
            ?x a ?type;
                skos:prefLabel ?label.
            FILTER(lang(?label) = "en" || lang(?label) = "fr").
            filter("{label}" in (ucase(str(?label)), lcase(str(?label)), str(?label))).
        }}
        """

    result = convert_sparql_to_json(sparqlQuery(g, q))

    if not result["results"]["bindings"]:
        old = previous + [label]
        df.append(old)

    for elt in result["results"]["bindings"]:
        #print(f'{label} ---> {elt["label"]["value"]}')
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
    if collection_name == "Annotation":

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

    db_name = "Ner"
    csv_files = glob.glob("./output/*.csv")
    clear_mongo_collection(db_name, "Annotation")
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
            load_csv_to_mongodb(csv, db_name, "Annotation")
        else:
            load_csv_to_mongodb(csv, db_name, "Metadata")

