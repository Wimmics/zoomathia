import os
import json
import logging
import requests
from pymongo import MongoClient
from collections import Counter

MONGO_URL = "mongodb://127.0.0.1:27017"
DB_NAME = "Ner"
SPARQL_ENDPOINT = "http://localhost:8080/sparql"
LANGUAGES = ["en", "fr", "it"]
TOP_N_PER_LANG = 100
CANDIDATE_POOL_SIZE = 500

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "web-app", "backend", "data", "top_concepts.json")

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def get_most_used_concept_uris():
    client = MongoClient(MONGO_URL)
    collection = client[DB_NAME]["Annotation"]

    counter = Counter()
    for doc in collection.find({}, {"concept_uri": 1}):
        counter[doc["concept_uri"]] += 1

    client.close()
    return counter.most_common(CANDIDATE_POOL_SIZE)


def fetch_labels(concept_uris):
    values = " ".join(f"<{uri}>" for uri in concept_uris)
    query = f"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?concept ?label ?type WHERE {{
  VALUES ?concept {{ {values} }}
  ?concept a ?type;
    skos:prefLabel ?label.
  FILTER(lang(?label) IN ({', '.join(f'"{l}"' for l in LANGUAGES)}))
}}"""
    response = requests.post(
        SPARQL_ENDPOINT,
        data={"query": query, "format": "json"},
        headers={"Accept": "application/sparql-results+json"},
        timeout=60
    )
    response.raise_for_status()
    return response.json()["results"]["bindings"]


def build_label_index(bindings):
    index = {}
    for row in bindings:
        concept = row["concept"]["value"]
        lang = row["label"]["xml:lang"]
        index.setdefault(concept, {})[lang] = {
            "label": row["label"]["value"],
            "type": row["type"]["value"]
        }
    return index


def main():
    logging.info("Counting concept usage in MongoDB Annotation collection...")
    top_concepts = get_most_used_concept_uris()
    logging.info(f"Found {len(top_concepts)} candidate concepts, fetching labels from Corese...")

    concept_uris = [uri for uri, _ in top_concepts]
    bindings = fetch_labels(concept_uris)
    label_index = build_label_index(bindings)

    result = {lang: [] for lang in LANGUAGES}
    for uri, count in top_concepts:
        labels = label_index.get(uri)
        if not labels:
            continue
        for lang in LANGUAGES:
            if len(result[lang]) >= TOP_N_PER_LANG:
                continue
            entry = labels.get(lang)
            if not entry:
                continue
            label = entry["label"] + " (Collection)" if entry["type"] == "http://www.w3.org/2004/02/skos/core#Collection" else entry["label"]
            result[lang].append({"label": label, "value": uri, "type": entry["type"], "count": count})

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    for lang in LANGUAGES:
        logging.info(f"{lang}: {len(result[lang])} top concepts written")
    logging.info(f"Written to {os.path.abspath(OUTPUT_PATH)}")


if __name__ == "__main__":
    main()
