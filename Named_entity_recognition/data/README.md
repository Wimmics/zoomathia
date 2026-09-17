# Le dossier `data`

Ce dossier contient tout ce qui touche au corpus de textes anciens du projet
Zoomathia : les textes eux-mêmes, le pipeline qui les traite, et le registre
qui les répertorie. Beaucoup d'autres fichiers présents ici sont des restes
de travail (brouillons, journaux d'exécution, scripts ponctuels) — ce README
distingue ce qui est important à comprendre de ce qui peut être ignoré.

## Les dossiers essentiels

### `zoo/`

Le corpus de référence, actuellement composé des textes dont l'original et
la traduction anglaise se correspondent parfaitement (voir
`repertoire_zoo/README.md` pour le détail de ce que ça veut dire et comment
c'est mesuré). Chaque œuvre a son propre sous-dossier `zooN/`, contenant un
fichier par témoin (l'original, sa traduction...).

Le nom de chaque fichier suit une convention fixe : `zooN/Xy.xml`, où `N` est
le numéro de l'auteur, `X` le numéro de l'œuvre parmi celles de cet auteur,
et `y` une lettre de langue (`g` grec, `l` latin, `e` anglais, `f` français,
`i` italien). Un chiffre en plus (`zoo16/1g_2.xml`) indique un deuxième
témoin dans la même langue pour la même œuvre. Cette convention, et le
registre qui l'attribue, sont documentés en détail dans
[`repertoire_zoo/README.md`](repertoire_zoo/README.md).

### `zoo_archive/`

Les autres textes du projet — ceux dont la traduction est incomplète,
générée par IA et non relue, ou dont le découpage ne correspond pas assez à
l'original pour un alignement fiable. Rien n'y est cassé ou à corriger
d'urgence : c'est juste un contenu qui n'atteint pas encore le niveau de
qualité du dossier `zoo/`. Même convention de nommage.

### `repertoire_zoo/`

Le système qui répertorie tous les auteurs, œuvres et fichiers, et qui
attribue à chacun son code `zooN/Xy`. Voir son propre
[README](repertoire_zoo/README.md) pour le détail complet — c'est le dossier
à lire en premier pour comprendre comment un texte est ajouté au projet.

### `pipeline_scripts/`

Les scripts qui transforment un fichier TEI du dossier `zoo/` en données
exploitables : reconnaissance d'entités nommées, alignement avec la
traduction humaine quand elle existe, génération des fichiers CSV de sortie.

- **`xml_to_csv.py`** — le script principal, celui qui fait tout le travail
  décrit ci-dessus. C'est le fichier le plus important du pipeline.
- **`tei_validator.py`** — vérifie qu'un fichier respecte bien le format TEI
  P5 avant de le traiter.
- **`morph_mongo.py`** — charge les résultats dans la base MongoDB du projet.
- **`beta-to-unicode.py`** — convertit le grec ancien saisi en notation
  "beta code" (une transcription en caractères latins, historiquement
  utilisée faute de clavier grec) vers de vrais caractères Unicode grecs.

### `output/`

Le résultat du pipeline : pour chaque fichier traité, quatre fichiers CSV
(`..._metadata.csv`, `..._paragraph.csv`, `..._link.csv`,
`..._annotations.csv`) contenant respectivement les informations générales
sur l'œuvre, le texte de chaque paragraphe, les liens entre divisions, et les
entités reconnues automatiquement dans chaque paragraphe.

### `mongo_loaded/`

Un fichier vide `.done` par texte déjà chargé dans MongoDB — sert juste de
pense-bête pour ne pas recharger deux fois le même texte.

### `TEI-P5/`

Des feuilles de style XSLT pour convertir d'anciens fichiers de l'ancien
format TEI P4 vers le format TEI P5 actuel.

## Les textes bruts, avant leur passage dans `zoo/`

**`texts/`** (la plus grande collection, organisée par identifiant `tlg`
pour le grec ou `phi` pour le latin) et **`animaux_encyclopedies/`** (des
encyclopédies médiévales sur les animaux) contiennent des textes sous leur
forme d'origine, avant d'être renommés selon la convention `zooN`.

(Le 2026-09-17, quatorze autres dossiers de ce type — `zoo24/`, `zoo42/`,
`zoo57/`, `zoo80/`, `phi0978/`, `tlg0059/`, `tlg0060/`, `tlg0074/`,
`tlg0084/`, `tlg0086/`, `tlg0093/`, `tlg0752/`, `stoa0216/` et
`a_verifier_7/` — ont été supprimés : une vérification antérieure, le
29/08, avait déjà confirmé que leur contenu était entièrement dupliqué dans
`zoo/`, et ils n'étaient de toute façon jamais suivis par Git.)

## Travaux en cours, pas encore finalisés

**`aelian_wip/`**, **`liber_animalibus_wip/`**, **`thomas_wip/`** — des
textes en cours de préparation, pas encore prêts à recevoir un code `zooN`
définitif.

## Le reste

De nombreux autres fichiers à la racine sont des restes de travail ponctuel
: des journaux d'exécution du pipeline (`*.log`), des listes de
correspondance utilisées pour des renommages en masse à un moment donné
(`*_prefix.txt`, `*_target.txt`), et quelques scripts ou dossiers de test
(`test/`, `LLM_NER/` — une approche alternative de reconnaissance d'entités
via un modèle de langage local). Rien de tout ça n'est nécessaire pour
comprendre ou faire fonctionner le projet au quotidien.
