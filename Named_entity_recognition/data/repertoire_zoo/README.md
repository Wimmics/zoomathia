La convention de numérotation `zooN` (attribution des numéros, structure des noms de
fichiers, table de correspondance) est documentée dans
[`Named_entity_recognition/data/README.md`](../Named_entity_recognition/data/README.md),
section « zoo ».

Ce dossier contient les scripts qui génèrent et maintiennent cette correspondance a
partir de 3 fichiers CSV tenus a jour directement sur Git (`auteurs_rows.csv`,
`oeuvres_rows.csv`, `fichiers_rows.csv`) : plus de base Supabase en ligne separee,
tout est sur Git.

- `ajouter_fichier.py` : ajoute un auteur/une oeuvre/un fichier (calcule le
  prochain identifiant disponible dans le CSV concerne, comme le ferait
  l'auto-increment d'une base de donnees), copie le fichier au bon endroit,
  regenere le registre, propose un commit/push.
- `generer_codes_zoo.py` : recalcule `repertoire_codes_zoo.csv` a partir des 3
  CSV ci-dessus, en y fusionnant la colonne `etat` (alignement
  original/traduction) tenue a part dans `alignement_zoo.csv` - cette derniere
  n'est jamais ecrasee par la regeneration.

Attention en equipe : ces 3 CSV n'ont plus de verrou centralise. Si deux
personnes ajoutent un auteur/une oeuvre en meme temps sans avoir recupere
(`git pull`) les derniers CSV, elles peuvent calculer le meme "prochain
identifiant" et entrer en collision - fais un `git pull` juste avant de
lancer `ajouter_fichier.py`.

`repertoire_codes_zoo.csv` est aussi lu par le pipeline principal
(`Named_entity_recognition/data/xml_to_csv.py` et `preparer_renommage.py`) via un
chemin relatif — ne pas déplacer ce dossier sans mettre à jour ces références.
