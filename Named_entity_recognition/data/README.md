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
