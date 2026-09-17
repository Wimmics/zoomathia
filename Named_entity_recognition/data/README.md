# The `data` folder

This folder contains everything related to the Zoomathia project's corpus of
ancient texts: the texts themselves, the pipeline that processes them, and
the registry that catalogs them.

## The essential folders

### `zoo/`

The reference corpus, currently made up of texts whose original and English
translation correspond perfectly. Each work has its own `zooN/` subfolder,
containing one file per witness (the original and its translation).

Each file name follows a fixed convention: `zooN/Xy.xml`, where `N` is the
author's number, `X` the number of the work among that author's works, and
`y` a language letter (`g` Greek, `l` Latin, `e` English). An extra digit
(`zoo16/1g_2.xml`) indicates a second witness in the same language for the
same work. This convention, and the registry that assigns it, are documented
in detail in [`repertoire_zoo/README.md`](repertoire_zoo/README.md).

### `zoo_archive/`

The rest of the project's texts: those whose translation is incomplete,
AI-generated, or whose segmentation doesn't match the original closely
enough for reliable alignment. Nothing here is broken or in urgent need of
fixing — it's simply content that hasn't yet reached the quality level of
the `zoo/` folder. Same naming convention.

### `repertoire_zoo/`

The system that catalogs every author, work, and file, and assigns each one
its `zooN/Xy` code. See its own [README.md](repertoire_zoo/README.md).

### `pipeline_scripts/`

The scripts that turn a TEI file from the `zoo/` folder into usable data:
named entity recognition, alignment with the human translation when one
exists, and generation of the output CSV files.

- **`xml_to_csv.py`** — the main script, the one that does all the work
  described above. It's the most important file in the pipeline.
- **`tei_validator.py`** — checks that a file properly conforms to the TEI
  P5 format before processing it.
- **`morph_mongo.py`** — loads the results into the project's MongoDB
  database.
- **`beta-to-unicode.py`** — converts ancient Greek entered in "beta code"
  notation (a transliteration into Latin characters, historically used for
  lack of a Greek keyboard) into actual Unicode Greek characters.

### `output/`

The pipeline's output: for each processed file, four CSV files
(`..._metadata.csv`, `..._paragraph.csv`, `..._link.csv`,
`..._annotations.csv`) containing, respectively, general information about
the work, the text of each paragraph, the links between divisions, and the
entities automatically recognized in each paragraph.

### `TEI-P5/`

XSLT stylesheets for converting old files from the former TEI P4 format to
the current TEI P5 format.

## The rest

Many other files at the root are leftovers from one-off work: pipeline
execution logs (`*.log`), correspondence lists used for mass renamings at
some point (`*_prefix.txt`, `*_target.txt`), and a few test scripts or
folders (`test/`, `LLM_NER/`, an alternative entity-recognition approach
using a local language model).
