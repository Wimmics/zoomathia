"""Remet MongoDB (base Ner, collection Annotation) dans l'etat que produirait le
chargement des CSV avec les filtres actuels de annotation_filters.py, sans
repasser par le NER ni par le thesaurus :
 - supprime les annotations que les filtres actuels refusent ;
 - reinsere les annotations DBpedia que des filtres plus stricts (ou des caches
   incomplets) avaient ecartees a tort et que les filtres actuels acceptent.
Usage : python3 reconcile_annotations.py [--dry-run]"""
import glob, json, os, re, sys, collections
import pandas as pd
from pymongo import MongoClient
from annotation_filters import keep_annotation

dry = '--dry-run' in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
coll = MongoClient()['Ner']['Annotation']
class_ok = json.load(open(os.path.join(HERE, 'dbpedia_cache.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, 'dbpedia_cache.json')) else {}

# 1. suppressions
present, to_delete = set(), []
for a in coll.find({}, {'paragraph_uri': 1, 'concept_uri': 1, 'mention': 1, 'origin': 1}):
    if keep_annotation(a['concept_uri'], a.get('mention'), a.get('origin')):
        present.add((a['paragraph_uri'], a['concept_uri']))
    else:
        to_delete.append(a['_id'])
print('a supprimer:', len(to_delete))

# 2. reinsertions depuis les CSV (DBpedia seulement)
to_insert = []
for path in sorted(glob.glob(os.path.join(HERE, 'output', '*_annotations.csv'))):
    try:
        df = pd.read_csv(path)
    except Exception:
        continue
    df = df[df['origin'] == 'DBpedia']
    seen = set()
    for row in df.itertuples(index=False):
        key = (row.paragraph_uri, row.concept_uri)
        if key in seen or key in present:
            continue
        if class_ok.get(row.concept_uri, True) is False:
            continue
        if keep_annotation(row.concept_uri, row.mention, 'DBpedia'):
            seen.add(key)
            m = str(row.mention)
            to_insert.append({'paragraph_uri': row.paragraph_uri, 'concept_uri': row.concept_uri, 'mention': m,
                              'score': float(row.score), 'origin': 'DBpedia', 'label': m})
print('a reinserer:', len(to_insert))
if not dry:
    for i in range(0, len(to_delete), 5000):
        coll.delete_many({'_id': {'$in': to_delete[i:i + 5000]}})
    for i in range(0, len(to_insert), 5000):
        coll.insert_many(to_insert[i:i + 5000])
    print('Annotation:', coll.estimated_document_count())
