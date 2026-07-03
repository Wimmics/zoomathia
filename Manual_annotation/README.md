# Manual Annotation

## Dependencies

The script works on Windows, using windows32com API.

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
