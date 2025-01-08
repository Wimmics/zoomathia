# Zoomathia Project
This work is carried out in the framework of the GDRI Zoomathia which aims to study the transmission of zoological knowledge from Antiquity to the Middle Ages. 

# Zoomathia Application

This application is being developed within the framework of the [HisINum project](https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/hisinum) funded by the [Academy of Excellence 5](https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux) of [IdEx UCA JEDI](https://univ-cotedazur.fr/recherche-innovation/defis-scientifiques-idex).

It aims to support the study of the transmission of zoological knowledge  from antiquity to the Middle Ages through the analysis of a corpus of  texts on animals compiled within the framework of the [Zoomathia GDRI](https://www.cepam.cnrs.fr/sites/zoomathia/presentation-generale-du-gdri-zoomathia/) funded by the CNRS.

It allows:

- exploration of the corpus, via a search for works by concept;
- exploration of a selected work from the corpus, with visualisation of the concepts annotating each of its parts;
- visualisation of the results of queries implementing competency questions on a selected work from the corpus.

It relies on the exploitation of a knowledge graph annotating the Zoomathia corpus of texts with concepts from the [TheZoo thesaurus](https://opentheso.huma-num.fr/opentheso/?idt=th310).
The pipeline for the automatic construction of this knowledge graph was developed within the framework of the [AutomaZoo project](https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/automazoo-annotation-automatique-dun-corpus-zoologique-ancien) funded by the Academy of Excellence 5 of IdEx UCA JEDI, and further refined within the framework of the HisINum project.
GitHub of the project: https://github.com/Wimmics/zoomathia

Access to the knowledge graph through its SPARQL endpoint:http://zoomathia.i3s.unice.fr/sparql

## Frontend

https://github.com/Wimmics/zoomathia/tree/main/web-app/web-zoomathia

## Backend

https://github.com/Wimmics/zoomathia/tree/main/web-app/backend

# Named Entity Recognition

## Dependencies
- pandas
```python
pip install pandas
```

- deep translator

```python
pip install deep-translator
```

- spacy (python 3.X < 3.13)

```shell
pip install spacy
pip install spacy-dbpedia-spotlight
pip install spacyfishing
```
models needed for spacy:

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
When the VM is launch, it will download the english knowledge base. You have to wait the end of this download and the launch of the service before using spacy NER.

- lxml-xml

```
pip install lxml
```

- PyMongo

```
pip install pymongo
```



## Pipeline

To use this pipeline of annotation, you have to start with the python script **xml_to_csv.py**. It will scan every folders at the same level of the script to find all XML file. The script will extract metadata of the work, work structure and paragraphs text. All work information will be transform into 4 csv files per XML file in the output folder:

- xxx_annotations.csv that contains all the annotation for the work
- xxx_link.csv that contains all information for the work structure
- xxx_metadata.csv contains all the metadata of the work (author, title, editor...)
- xxx_paragraph.csv contains all the paragraph of the work

When the xml_to_csv process is over, the next step is to launch the **morph_mongo.py** script that upload all the generated CSV to its respective MongoDB  collection. This process will also filter annotation based on **classes URI** specified in the **filter_class.json** file and find close concept base on the label in the TheZoo Thesaurus.

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

The last step after the morph_mongo process is the graph generation with morph-xR2RML in the rules folder. Every file has to be specified in the morph.properties file:

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

The produced graph will be formed with 5 turtle files. The vocab.ttl file contains all the DBpedia alignment with TheZoo thesaurus. 

# Manual Annotation

## Dependencies

The script only work with windows due to strong optimisation only available on windows32com API.

- pandas

```python
pip install pandas
```

- pywin32

```
pip install pywin32
```

- opendocx

```
pip install python-docx
```



## Pipeline

The script extract text annotation label from TheZoo thesaurus in docx comments based on the following pattern:

```
concept label
parent label : child label : grand child label
concept label1 ; concept label2
```

All labels extracted will be match with a concept in TheZoo if it's label is close enough. The script will generate multiple CSV file to generate graph and correct error of matching label.

The last step are the manual upload of the file in MongoDB Collection "Paragraphe" and "Annotation" and the graph generation with morph-xR2RML in the rules folder. Every file has to be specified in the morph.properties file:

```yaml
# xR2RML mapping file. Mandatory.
mappingdocument.file.path=paragraph.ttl
#mappingdocument.file.path=annotation.ttl

# -- Where to store the result of the processing. Default: result.txt
output.file.path=output/paragraph.ttl
#output.file.path=output/annotation.ttl
```

