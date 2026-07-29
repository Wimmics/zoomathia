## TEI-P5

This directory contains xsl stylesheet to convert xml files from TEI-P4 to TEI-P5 format.

## thesaurus

Contains concepts intended to be added to the thesaurus later.

## metrics

Contains different statistics on the results of the pipeline.

## texts

Contains all the texts to be annotated. The directories begins by "phi" contains the latin texts and - is available - their translation. Idem with "tlg" but for greek texts - tlg stands for "Thesaurus Linguae Graecae".

## Data

The ancient texts are in the directories that begins with `phi` for latin texts and `tlg` for greek texts. The greek texts must be and are currently encoded in Unicode to be translated automaticly with Google Translate.
The texts mainly comes from the [Perseus](https://github.com/PerseusDL/canonical-greekLit) project.

## Output

The result of the `xml_to_csv.py` program can be seen in the `output` directory. It contains all the csv files ment to be process by the `morph_mongo.py` program.

## zoo
Contains all the texts that have been catalogued and encoded in TEI-P5, reorganized under a new internal identification system, in addition to the existing `tlg-`/`phi-`/`sto-` identifiers.

Each file is named following the pattern:
- `author_number`: sequential number assigned to the author (corresponds to the `id` in the `auteurs` table in Supabase)
- `work_number`: sequential number assigned to the work, specific to each author (position among that author's works, ordered by their `id` in the `oeuvres` table)
- `language_code`: `g` (Greek), `l` (Latin), `e` (English), `f` (French), `i` (Italian)

Example: `zoo1/1e.xml` is the English translation of the first work of author #1.

When several files share the same code (multiple editions or translations in the same language for the same work), a numeric suffix is added: `zoo16/1g_1.xml`, `zoo16/1g_2.xml`, etc.

The correspondence table between the new `zoo` codes, the file names, and the original `tlg`/`phi` identifiers is maintained in the `auteurs`, `oeuvres` and `fichiers` tables on Supabase, and can be regenerated as a CSV file (`repertoire_codes_zoo.csv`) using the scripts in `repertoire_zoo/`.

