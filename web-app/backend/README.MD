# Zoomathia backend API



## Requirement

To run the server properly, you need a version of nodeJS above 14.x. By default on Ubuntu build, the package only install the LTS nodeJS 12.22.9 version which does not support "[?](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)" optional chaining operations. To install a more recent version of NodeJS:

0. Install curl on your system if it's not already the case

```shell
sudo apt-get install -y curl
```

1. Download the setup script of nodeJS

```shell
curl -fsSL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh
```

2. Run the setup script with sudo privilege:


```sh
sudo -E bash nodesource_setup.sh
```

3. Install NodeJS

```shell
sudo apt-get install -y nodejs
```

4. Verify the version (have to be above 14.x)

```shell
node -v
```

For other OS distribution, you can follow the steps here -> https://github.com/nodesource/distributions?tab=readme-ov-file#debian-and-ubuntu-based-distributions



## Run the backend API

1. Install all ExpressJS dependencies

```shell
npm install
```

2. Run the ExpressJS App

```shell
npm start
```

## Routes

### GET

- /download-xml?file
- /getMetadata?uri
- /getSummary?uri
- /getWorkPart?title
- /getAuthors
- /getWorksFromAuthors?author
- /getWorks
- /getWorkByUri?uri
- /getChildrenType?uri
- /getChildren?uri
- /getParagraphs?uri
- /getCurrentType?uri
- /getParagraphAlone?uri
- /getConcepts?uri&lang
- /searchConcepts?input
- /getLanguageConcept
- /getTheso?lang
- /qcList
- /getQCspo
- /getQC?id
- /download-custom-search-json?sparql
- /download-turtle?uri
- /download-custom-search-csv?sparql
- /download-qc-json?id
- /download-qc-csv?id

### POST

- /getParagraphWithConcept
- /getParagraphsWithConcepts
- /customSearch
