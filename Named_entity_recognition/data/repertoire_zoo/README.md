# Le registre repertoire_zoo

Ce dossier tient à jour la liste de tous les auteurs, œuvres et fichiers du
corpus Zoomathia, et attribue à chacun un code court et unique du genre
`zoo57/9g` — ce code sert ensuite de nom de dossier et de fichier partout
ailleurs dans le projet (`Named_entity_recognition/data/zoo/zoo57/9g.xml`).

Tout repose entièrement sur Git : il n'y a plus de base de données en ligne
séparée à laquelle se connecter. Les fichiers de ce dossier *sont* la
référence — pas une copie d'autre chose.

## Comment lire le code `zoo57/9g`

Chaque code se décompose en trois informations :

- **`57`** : le numéro de l'auteur (Xénophon, par exemple, porte le numéro 57
  dans ce système — un numéro purement interne au projet, sans rapport avec
  un quelconque classement officiel).
- **`9`** : le numéro d'ordre de l'œuvre parmi celles de cet auteur déjà
  enregistrées (sa 9ᵉ œuvre ajoutée au système, pas forcément la 9ᵉ dans
  l'ordre chronologique de composition).
- **`g`** : la langue du fichier — `g` pour grec, `l` pour latin, `e` pour
  anglais, `f` pour français, `i` pour italien.

Si plusieurs fichiers existent dans la même langue pour la même œuvre (par
exemple deux manuscrits grecs différents du même texte), le deuxième reçoit
un suffixe `_2`, le troisième `_3`, et ainsi de suite. Le tout premier
fichier n'a jamais de suffixe.

## Les fichiers de ce dossier

### Les données (les vrais fichiers de référence)

**`auteurs_rows.csv`** — la liste de tous les auteurs anciens du projet
(Aristote, Xénophon, etc.), un par ligne, avec son numéro.

**`oeuvres_rows.csv`** — la liste de toutes les œuvres, reliées à leur
auteur (chaque ligne dit "cette œuvre appartient à cet auteur-là").

**`fichiers_rows.csv`** — la liste de tous les fichiers XML concrets (un
texte grec, sa traduction anglaise...), reliés à leur œuvre. Chaque ligne de
ces trois tables a un identifiant numérique (colonne `id`), qui sert de base
au calcul du code `zooN`.

**`alignement_zoo.csv`** — un quatrième fichier, à part, qui garde une note
sur la qualité de la correspondance entre chaque texte original et sa
traduction anglaise (`Complet`, `Partiel (XX%)`, `IA non relue`, `Sans
traduction anglaise`...). Il est tenu séparément des trois tables ci-dessus
parce que cette information n'a rien à voir avec l'identité d'un auteur ou
d'une œuvre — c'est une observation qu'on a faite après coup en comparant
les textes entre eux.

### Le résultat calculé automatiquement

**`repertoire_codes_zoo.csv`** — le tableau final, obtenu en combinant les
quatre fichiers ci-dessus : une ligne par fichier, avec son code `zooN/Xy`,
le nom de l'auteur, le titre de l'œuvre, et l'état d'alignement repris
depuis `alignement_zoo.csv`. C'est ce fichier qu'utilisent les autres
scripts du projet (`Named_entity_recognition/data/xml_to_csv.py`,
`preparer_renommage.py`) — **il ne faut jamais le modifier à la main**,
puisqu'il est entièrement recalculé à chaque fois qu'on relance
`generer_codes_zoo.py`, et toute modification manuelle serait alors perdue.

### Les scripts (les programmes)

**`generer_codes_zoo.py`** — calcule `repertoire_codes_zoo.csv` à partir des
quatre fichiers de données. On peut le relancer à tout moment sans risque
(`python3 generer_codes_zoo.py`) : il ne fait que lire les CSV et réécrire
le résultat.

**`ajouter_fichier.py`** — le programme à lancer pour ajouter un nouveau
texte au projet (auteur, œuvre, fichier). Voir la section suivante pour le
détail de ce qu'il fait.

## Ajouter un nouveau fichier, étape par étape

On lance le script depuis ce dossier :

```
cd Named_entity_recognition/data/repertoire_zoo
git pull                     # important, voir la mise en garde plus bas
python3 ajouter_fichier.py
```

**Étape 1 — l'auteur.** Le script demande le nom de l'auteur (par exemple
"ARISTOTELES"). Il cherche ce nom dans `auteurs_rows.csv` :

- S'il le trouve, il affiche son numéro existant et demande de le
  confirmer — rien n'est créé, on réutilise l'auteur déjà là.
- S'il ne le trouve pas, il demande deux informations pour créer sa fiche :
  un **identifiant de référence** comme `tlg0086` (un code utilisé par les
  spécialistes pour désigner un auteur ancien de façon unique — un peu comme
  un ISBN pour un livre ; on peut laisser vide si l'auteur n'en a pas), et
  une **période historique** approximative ("antique", "tardo-antique",
  "médiéval"). Le script attribue alors à cet auteur un numéro tout seul :
  il regarde le plus grand numéro déjà utilisé dans `auteurs_rows.csv` (89,
  par exemple) et donne au nouvel auteur ce nombre plus un (90) — pour être
  certain de ne jamais réutiliser un numéro déjà pris.

**Étape 2 — l'œuvre.** Même logique : le script montre les œuvres déjà
enregistrées pour cet auteur, et on choisit soit une existante, soit on en
crée une nouvelle (titre original, langue d'origine) — avec, là aussi, un
numéro d'ordre attribué automatiquement.

**Étape 3 — le fichier.** On indique son nom, sa langue, et sa source (d'où
vient le texte : Perseus, First1KGreek, une édition imprimée...).

**Étape 4 — le code final.** Le script assemble tout ça en un code
`zooN/Xy` et régénère immédiatement `repertoire_codes_zoo.csv` pour que le
registre reflète ce changement sans délai.

**Étape 5 — placer le fichier et partager.** Le script demande où se trouve
le fichier XML à ajouter, le copie au bon endroit
(`Named_entity_recognition/data/zoo/zooN/Xy.xml`), puis propose de faire le
commit (avec un message rédigé automatiquement) et, si on confirme, de le
pousser sur GitHub. Tant que ce push n'est pas fait, le reste de l'équipe ne
voit rien de ce changement.

## Une mise en garde importante pour le travail en équipe

Comme il n'y a plus de base de données centrale pour gérer les numéros, deux
personnes qui ajouteraient un auteur ou une œuvre exactement en même temps,
sans avoir récupéré les derniers changements (`git pull`), pourraient
chacune calculer le même "prochain numéro disponible" et se retrouver en
conflit (deux auteurs différents avec le même numéro). C'est pour ça qu'il
faut toujours faire un `git pull` juste avant de lancer `ajouter_fichier.py`
— avec le rythme d'ajout actuel du projet (quelques textes de temps en
temps, pas des dizaines par jour), ce risque reste faible mais reste bon à
connaître.
