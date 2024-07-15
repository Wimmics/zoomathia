import pandas as pd
from pymongo import MongoClient
import os
import glob


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
    # Conversion du DataFrame en dictionnaires et insertion dans MongoDB
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
    db_name = "Ner"
    csv_files = glob.glob("*.csv")
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
        elif "annotation" in csv:
            load_csv_to_mongodb(csv, db_name, "Annotation")
        else:
            load_csv_to_mongodb(csv, db_name, "Metadata")

