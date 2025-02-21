# Zoomathia Application

This application is being developed within the framework of the [HisINum project](https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/hisinum) funded by the [Academy of Excellence 5](https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux) of [IdEx UCA JEDI](https://univ-cotedazur.fr/recherche-innovation/defis-scientifiques-idex).

It aims to support the study of the transmission of zoological knowledge  from antiquity to the Middle Ages through the analysis of a corpus of  texts on animals compiled within the framework of the [Zoomathia GDRI](https://www.cepam.cnrs.fr/sites/zoomathia/presentation-generale-du-gdri-zoomathia/) funded by the CNRS.

It allows:

- exploration of the corpus of ancient texts, via a concept-based search for works;
- exploration of a selected work by visualizing the concepts annotating each of its parts;
- visualisation of the results of queries implementing competency questions on a selected work.

It relies on the exploitation of a knowledge graph annotating the Zoomathia corpus of texts with concepts from the [TheZoo thesaurus](https://opentheso.huma-num.fr/opentheso/?idt=th310).
The pipeline for the automatic construction of this knowledge graph was developed within the framework of the [AutomaZoo project](https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/automazoo-annotation-automatique-dun-corpus-zoologique-ancien) funded by the Academy of Excellence 5 of [IdEx UCA JEDI](https://univ-cotedazur.fr/recherche-innovation/defis-scientifiques-idex), and further refined within the framework of the HisINum project.

Access to the knowledge graph through its SPARQL endpoint:http://zoomathia.i3s.unice.fr/sparql

The Zoomathia application is split in two different folder: (1) the frontend side and (2) the backend side.

## Frontend

The frontend application contains the implementation of the interaction and visual design that hide SPARQL requests from non-expert of web semantics. It was implemented in React.js, the components are fed with the data contained in the knowledge graph.

To try the frontend application, follow the readme: https://github.com/Wimmics/zoomathia/tree/main/web-app/web-zoomathia

## Backend

The backend application contains the services that map SPARQL queries to JSON objects, needed by the components of the frontend. 

To try the backend application, follow the readme: https://github.com/Wimmics/zoomathia/tree/main/web-app/backend


# Named Entity Recognition annotation pipeline

## Dependencies

```python
pip install pandas
pip install deep-translator
pip install lxml
pip install pymongo
```

- spacy (python 3.X < 3.13)

```shell
pip install spacy
pip install spacy-dbpedia-spotlight
pip install spacyfishing
```
- models needed for spacy:

```shell
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_sm
```

- dbpedia_spotlight docker

```shell
# pull the official image
docker pull dbpedia/dbpedia-spotlight
# create a volume for persistently saving the language models
docker volume create spotlight-models
# start the container (here assuming we want the en model, but any other supported language code can be used)
docker run -ti --restart unless-stopped --name dbpedia-spotlight.en --mount source=spotlight-models,target=/opt/spotlight -p 2222:80 dbpedia/dbpedia-spotlight spotlight.sh en
```
When the VM starts, it will download the English knowledge base. 
Wait until the download completes and the service starts up before using spacy NER.


## Annotation pipeline

### XML to CSV transformation

To use this pipeline of annotation, you have to start with the python script `Named_entity_recognition/data/original_files/xml_to_csv.py`. It will scan every folders at the same level of the script to find all XML files. For each work the script will extract the metadata, structure and paragraphs. All work information will be transformed into 4 csv files per XML file in the `output` folder:

- xxx_annotations.csv that contains all the annotation for the work
- xxx_link.csv that contains all information for the work structure
- xxx_metadata.csv contains all the metadata of the work (author, title, editor...)
- xxx_paragraph.csv contains all the paragraph of the work

### Load CSV to MongoDB

The next step is to launch the `Named_entity_recognition/data/original_files/morph_mongo.py` script that uploads all the generated CSV files into respective MongoDB collections. This process will also filter out annotations based on the class URIs specified in the `filter_class.json` file and find close concepts base on the label in the TheZoo Thesaurus.

```json
{
    "class": [
        "<http://dbpedia.org/class/yago/WikicatAnimatedCharacters>",
        "<http://dbpedia.org/class/yago/WikicatTelevisionCharacters>",
        "<http://dbpedia.org/class/yago/WikicatTheSimpsonsCharacters>",
        ...
    ]
}
```

### Generate RDF files

The last step is the graph generation with Morph-xR2RML in the `Named_entity_recognition/rules`  folder. Every file has to be specified in the `tei/morph.properties `file:

```yaml
# xR2RML mapping file. Mandatory.
mappingdocument.file.path=paragraph.ttl
#mappingdocument.file.path=link.ttl
#mappingdocument.file.path=metadata.ttl
#mappingdocument.file.path=annotation.ttl
#mappingdocument.file.path=vocab.ttl

# -- Where to store the result of the processing. Default: result.txt
output.file.path=output/paragraph.ttl
#output.file.path=output/link.ttl
#output.file.path=output/metadata.ttl
#output.file.path=output/annotation.ttl
#output.file.path=output/vocab.ttl
```

The produced graph will be formed of 5 turtle files. The vocab.ttl file contains all the DBpedia alignments with TheZoo thesaurus. 


# Manual Annotation

## Dependencies

The script only works on Windows due to strong optimisation only available on windows32com API.

```python
pip install pandas
pip install pywin32
pip install python-docx
```

## Directories

- QC: contains a Jupyter Notebook with the SPARQL implementation of the competency questions to evaluate the graph.
- Script: contains docx files to be extracted, the extraction pipeline script `extraction.py` and the csv output of the extraction, needed for Morph-xR2RML.
- ontology: contains all the Tutle files generated.
- mapping: contains all xR2RML mapping files to build the graph


## Pipeline

The script extracts text annotation labels from TheZoo thesaurus in docx comments based on the following pattern:

```
concept label
parent label : child label : grand child label
concept label1 ; concept label2
```

All labels extracted will be matched with a concept of TheZoo if its label is close enough. 
The script will generate multiple CSV files to generate graph and correct error of matching label.

The last step is the manual upload of the files in MongoDB collections "Paragraphe" and "Annotation", and the graph generation with Morph-xR2RML in the folder `Named_entity_recognition/rules`. Every file has to be specified in file `morph.properties`:

```yaml
# xR2RML mapping file. Mandatory.
mappingdocument.file.path=paragraph.ttl
#mappingdocument.file.path=annotation.ttl

# -- Where to store the result of the processing. Default: result.txt
output.file.path=output/paragraph.ttl
#output.file.path=output/annotation.ttl
```
