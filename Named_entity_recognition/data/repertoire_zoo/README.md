# The repertoire_zoo registry

This folder keeps an up-to-date list of every author, work, and file in the
Zoomathia corpus, and assigns each one a short, unique code such as
`zoo57/9g`. This code is then used as the folder and file name everywhere
else in the project (`Named_entity_recognition/data/zoo/zoo57/9g.xml`).


## How to read the code `zoo57/9g`

Each code breaks down into three pieces of information:

- **`57`**: the author's number (Xenophon, for instance, is number 57 in
  this system, a number purely internal to the project, unrelated to any
  official classification).
- **`9`**: the ordinal number of the work among those already registered for
  this author (the 9th work added to the system, not necessarily the 9th in
  chronological order of composition).
- **`g`**: the file's language `g` for Greek, `l` for Latin, `e` for
  English.

If several files exist in the same language for the same work (for example
two different Greek manuscripts of the same text), the second one gets a
`_2` suffix, the third a `_3`, and so on. The very first file never has a
suffix.

## The files in this folder

### The data (the actual reference files)

**`auteurs_rows.csv`**: the list of every ancient author in the project
(Aristotle, Xenophon, etc.), one per line, with their number.

**`oeuvres_rows.csv`**: the list of every work, linked to its author (each
line says "this work belongs to that author").

**`fichiers_rows.csv`**: the list of every concrete XML file (a Greek text,
its English translation...), linked to its work. Each row in these three
tables has a numeric identifier (the `id` column), which is used as the
basis for computing the `zooN` code.

**`alignement_zoo.csv`**: a fourth, separate file that keeps a note on the
quality of the match between each original text and its English translation
(`Complet`, `Partiel (XX%)`, `IA non relue`, `Sans traduction anglaise`).

### The automatically computed result

**`repertoire_codes_zoo.csv`**: the final table, obtained by combining the
four files above: one row per file, with its `zooN/Xy` code, the author's
name, the work's title, and the alignment status taken from
`alignement_zoo.csv`. This is the file used by the project's other scripts
(`Named_entity_recognition/data/xml_to_csv.py`, `preparer_renommage.py`)
**it should never be edited by hand**, since it's entirely recomputed every
time `generer_codes_zoo.py` is run, and any manual edit would then be lost.

### The scripts (the programs)

**`generer_codes_zoo.py`**: computes `repertoire_codes_zoo.csv` from the
four data files. It can be re-run at any time without risk
(`python3 generer_codes_zoo.py`): it only reads the CSVs and rewrites the
result.

**`ajouter_fichier.py`**: the program to run to add a new text to the
project (author, work, file). See the next section for the detail of what
it does.

## Adding a new file, step by step

The script is run from this folder:

```
cd Named_entity_recognition/data/repertoire_zoo
git pull                     # important, see the warning below
python3 ajouter_fichier.py
```

**Step 1 — the author.** The script asks for the author's name (e.g.
"ARISTOTELES"). It looks up this name in `auteurs_rows.csv`:

- If it finds it, it shows the existing number and asks for confirmation —
  nothing is created, the existing author is reused.
- If it doesn't find it, it asks for two pieces of information to create
  their entry: a **reference identifier** such as `tlg0086` (a code used by
  specialists to uniquely designate an ancient author a bit like an ISBN
  for a book; it can be left blank if the author doesn't have one), and an
  approximate **historical period** ("antique", "late antique",
  "medieval"). The script then assigns this author a number on its own: it
  looks at the highest number already used in `auteurs_rows.csv` (89, for
  instance) and gives the new author that number plus one (90) to make
  sure a number already taken is never reused.

**Step 2 — the work.** Same logic: the script shows the works already
registered for this author, and you either pick an existing one or create a
new one (original title, original language) with, again, an ordinal number
assigned automatically.

**Step 3 — the file.** You indicate its name, its language, and its source
(where the text comes from: Perseus, First1KGreek, a printed edition...).

**Step 4 — the final code.** The script assembles all this into a
`zooN/Xy` code and immediately regenerates `repertoire_codes_zoo.csv` so the
registry reflects this change without delay.

**Step 5 — placing the file and sharing it.** The script asks where the XML
file to add is located, copies it to the right place
(`Named_entity_recognition/data/zoo/zooN/Xy.xml`), then offers to make the
commit (with an automatically written message) and, if confirmed, to push it
to GitHub.
