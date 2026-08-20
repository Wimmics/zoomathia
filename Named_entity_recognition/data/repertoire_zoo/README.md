La convention de numérotation `zooN` (attribution des numéros, structure des noms de
fichiers, table de correspondance) est documentée dans
[`Named_entity_recognition/data/README.md`](../Named_entity_recognition/data/README.md),
section « zoo ».

Ce dossier contient les scripts qui génèrent et maintiennent cette correspondance à
partir des tables Supabase (`auteurs`, `oeuvres`, `fichiers`), exportées ici en CSV.

Attention : `repertoire_codes_zoo.csv` est aussi lu par le pipeline principal
(`Named_entity_recognition/data/xml_to_csv.py` et `preparer_renommage.py`) via un
chemin relatif — ne pas déplacer ce dossier sans mettre à jour ces références.
