# Zoomathia backend application

## Requirement

To run the server, you need a version of **nodeJS above 14.x**. By default on Ubuntu build, the package only installs the LTS nodeJS 12.22.9 version which does not support "[?](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)" optional chaining operations. To install a more recent version of NodeJS:

- Download the setup script of nodeJS

```shell
curl -fsSL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh
```

- Run the setup script with sudo privilege:

```sh
sudo -E bash nodesource_setup.sh
```

- Install NodeJS

```shell
sudo apt-get install -y nodejs
```

- Verify the version (have to be above 14.x)

```shell
node -v
```

For other OS distributions, follow the steps here -> https://github.com/nodesource/distributions?tab=readme-ov-file#debian-and-ubuntu-based-distributions



## Run the backend application

1. Install all ExpressJS dependencies

```shell
npm install
```

2. Run the ExpressJS App

```shell
npm start
```

The app will be accessible at `http://localhost:3001`.

## API documentation

### HTTP GET

- `/download-xml?file`: Download the xml file of the work. The filename is contained in the graph.
- `/getMetadata?uri`: Get the metadata of the given work URI. Return a JSON object.
```js
response = {
      author: elt?.author.value,
      editor: elt?.editor.value,
      date: elt?.date.value,
      file: elt?.file.value
    }
```

- `/getSummary?uri`: Get structure hierarchy of a work. Mostly used to generate Table Of Content components.
Return imbriqued JSON Object..
```js
response[elt?.current.value] = {
      uri: elt?.current.value,
      id: elt?.id.value,
      title: elt?.title.value,
      type: elt?.type.value,
      children: []
    }
```

- `/getWorkPart?title`: Get direct children of a given URI
```js
    {
      uri: elt["part"]["value"],
      id: elt["id"]["value"],
      title: elt["title"]["value"],
      type: elt['type'].value
    }
```
- `/getAuthors`: Get author list of works
```js
[{ name: author.name.value }, ...]
```

- `/getWorksFromAuthors?author`: Filter works based on the given author
```js
    {
      uri: elt?.oeuvre.value,
      title: elt?.title.value,
      author: req.query.author
    }
```
- `/getWorks` List all works
```js
    {
      uri: elt?.oeuvre.value,
      title: elt?.title.value,
      author: elt?.author.value
    }
```
- `/getWorkByUri?uri`: Retrieve author and work metadata based on the given URI
```js
    {
      uri: elt.work.value,
      title: elt.title.value,
      author: elt.author.value
    }
```

- `/getChildrenType?uri`: Get all RDF classes of children from the given URI (Use for component logic)

- `/getChildren?uri`: List all direct children of the given URI
```js
    {
      uri: elt?.child.value,
      title: elt?.title.value,
      type: elt?.type.value
    }
```
- `/getParagraphs?uri`: Get all direct paragraph from the given URI
```js
    {
      title: elt?.title.value,
      uri: elt?.uri.value,
      text: elt?.text.value,
      id: elt?.id.value
    }
```
- `/getCurrentType?uri`: Get RDF classes of the current URI

- `/getParagraphAlone?uri`: **Obsolete** Retrieve paragraphs from the given hierarchical URI.

```js
    {
      uri: elt?.paragraph.value,
      text: elt?.text.value,
      id: elt?.id.value
    }
```
- `/getConcepts?uri&lang`: List all concept annotation from the paragraph in the given current lang. The lang is automatically set to English if no skos:prefLabel is avalaible in the choosen language.
```js
annotations[elt?.label.value] = {
      concept: elt?.concept.value,
      label: elt?.label.value,
      type: elt?.annotation_type.value,
      offset: []
    }
```
- `/searchConcepts?input`: List all concepts that match the language and labels given
```js
    {
      uri: elt?.concept.value,
      label: elt?.label.value
    }
```

- `/getLanguageConcept`: Change label language of concepts
```js
```
- `/getTheso?lang`: List all concepts and collections of the TheZoo thesaurus
```js
    {
      label: elt?.type.value === "http://www.w3.org/2004/02/skos/core#Collection" ? elt?.label.value + " (Collection)": elt?.label.value,
      value:elt?.concept.value,
      type: elt?.type.value
    }
```
- `/qcList`: Get list of Competency Questions stored in the qcs.js file (queries folder)
```js
    {
        id:
        file:
        title:
        vizuTitle:
        goal:
    }
```
- `/getQCspo`: Return SPARQL result of the MGExplorer version of SPARQL query QC

- `/getQC?id`: Get the SPARQL result of SPARQL query of the QC

- `/download-custom-search-json?sparql`
- `/download-turtle?uri`
- `/download-custom-search-csv?sparql`
- `/download-qc-json?id`
- `/download-qc-csv?id`

### HTTP POST

- `/getParagraphWithConcept`: Get all paragraph from the given parent URI if the given concept is present in the annotations.

```js
    {
        uri: elt?.paragraph.value,
        text: elt?.text.value,
        title: elt?.title.value,
        id: elt?.id.value
    }
 ```
- `/getParagraphsWithConcepts`: Get all paragraphs which contains the given concepts presents in its annotations

```js
    {
        author: elt?.author.value,
        bookUri: elt?.uri.value,
        bookId: elt?.book.value,
        title: elt?.title.value,
        uri: elt?.paragraph.value,
        text: elt?.text.value,
        id: elt?.id.value
    }
```
- `/customSearch`: Generate all data needed to build sub-corpus. Return a tree that contain all work to paragraph metadata.
