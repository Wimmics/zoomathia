"""Applique a posteriori les filtres d'annotation_filters.py aux annotations deja
chargees dans MongoDB (base Ner, collection Annotation), sans repasser par le NER.
Usage : python3 apply_annotation_filters.py [--dry-run] [prefixe_uri_a_ignorer ...]
Les documents supprimes sont sauvegardes (JSON) dans le dossier courant."""
import sys, json, collections, time
from pymongo import MongoClient
from annotation_filters import keep_annotation

args = [a for a in sys.argv[1:] if not a.startswith('--')]
dry = '--dry-run' in sys.argv
coll = MongoClient()['Ner']['Annotation']
skip = tuple(args)
to_delete, backup = [], []
kept = collections.Counter()
for a in coll.find({}, {'paragraph_uri': 1, 'concept_uri': 1, 'mention': 1, 'origin': 1, 'score': 1}):
    if skip and a['paragraph_uri'].startswith(skip):
        continue
    if keep_annotation(a['concept_uri'], a.get('mention'), a.get('origin')):
        kept[a.get('origin')] += 1
    else:
        to_delete.append(a['_id'])
        backup.append({k: a.get(k) for k in ('paragraph_uri', 'concept_uri', 'mention', 'origin', 'score')})
print('a supprimer:', len(to_delete), '| conservees:', dict(kept))
if not dry and to_delete:
    name = 'annotations_filtrees_%s.json' % time.strftime('%Y%m%d_%H%M%S')
    json.dump(backup, open(name, 'w', encoding='utf-8'), ensure_ascii=False)
    for i in range(0, len(to_delete), 5000):
        coll.delete_many({'_id': {'$in': to_delete[i:i + 5000]}})
    print('supprimees, sauvegarde:', name)
