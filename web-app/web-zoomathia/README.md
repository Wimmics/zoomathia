# Frontend application

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## React scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode. 
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.
The build is minified and the filenames include the hashes.



## Components list

### Competency Questions Component

Display the page of Competency Question visualisation. The component is divided into 3 parts, an input select to select the question, a Table of the raw SPARQL result and a zone that use MGExplorer visualisation.

Routes: `/qcList`, `/getQC`, `/getQCspo`, `/download-qc-json`, `/download-qc-csv`

### Display Search Component

Build the grid that display book structure and paragraph with annotation for the "Explore the Corpus" page.

- route used: no route used. The component information is fed and does not fetch anything.
- 
### Display Text Component
Build the text visualisation of a single Work. This component use the "section component" for the book structure before the "Paragraph display component"

Routes: `/getMetadata`, `/getSummary`, `/download-xml`, `/download-turtle`

### Explore Component

Build the page "Explore a Work". This component is the mother component to dislay text for a single Work.

Routes: `/getWorkPart`, `/getWorksFromAuthors`, `/getWorks`, `/getAuthors`, `/getWorkByUri`

### Paragraph Component

Build the Paragraph component that show the text, id and annotations.

Route: `/getConcepts`
  
### Search Component

Build the page "Explore the Corpus". The component is divide in 2 big part, the search input part with 3 inputs: authors, work and concepts; and a second part which show the results corpus based on the filter given.

Routes: `/getAuthors`, `/getWorks`, `/getTheso`, `/download-custom-search-json`, `/download-custom-search-csv`, `/customSearch`

### Section Component

Build the header of the current work structure part (chapter title, book title etc) before display Paragraph.

Routes: `/getChildren`, `/getConcepts`, `/getParagraphs`, `/getChildrenType`, `/getCurrentType`

### Table of Content 

Build the table of content of the given work list structure

Route: no fetch

### Tooltip

Build tooltip of the "Explore the corpus" page

Route: no fetch
  
### Work Component (obsolete)

Show text paragraph and annotation from the given URI

Routes: `/getParagraphAlone`, `/getConcepts`
