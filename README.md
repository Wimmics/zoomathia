# zoomathia
Zoomathia
This work is carried out in the framework of the GDRI Zoomathia which aims to study the transmission of zoological knowledge from Antiquity to the Middle Ages. 

## Dependencies
- pandas
- deep translator
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

dbpedia_spotlight docker
```shell
# pull the official image
docker pull dbpedia/dbpedia-spotlight
# create a volume for persistently saving the language models
docker volume create spotlight-models
# start the container (here assuming we want the en model, but any other supported language code can be used)
docker run -ti --restart unless-stopped --name dbpedia-spotlight.en --mount source=spotlight-models,target=/opt/spotlight -p 2222:80 dbpedia/dbpedia-spotlight spotlight.sh en
```
When the VM is launch, it will download the english knowledge base. You have to wait the end of this download and the lauche of the service before using spacy NER.

- lxml-xml