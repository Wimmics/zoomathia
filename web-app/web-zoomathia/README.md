# Getting Started with React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)

## Components list

### Competency Questions Component

Display the page of Competency Question visualisation. The component is divide in 3 part, an input select to select the question, a Table of the raw SPARQL result and a zone that use MGExplorer visualisation.

- route used: /qcList, /getQC, /getQCspo, /download-qc-json, /download-qc-csv

### Display Search Component

Build the grid that display book structure and paragraph with annotation for the "Explore the Corpus" page.

- route used: no route used. The component information is fed and does not fetch anything.
- 
### Display Text Component
Build the text visualisation of a single Work. This component use the "section component" for the book structure before the "Paragraph display component"

- route used: /getMetadata, /getSummary, /download-xml, /download-turtle
### Explore Component

Build the page "Explore a Work". This component is the mother component to dislay text for a single Work.

- route used: /getWorkPart, /getWorksFromAuthors, /getWorks, /getAuthors, /getWorkByUri

### Paragraph Component

Build the Paragraph component that show the text, id and annotations.

- route used: /getConcepts
  
### Search Component

Build the page "Explore the Corpus". The component is divide in 2 big part, the search input part with 3 inputs: authors, work and concepts; and a second part which show the results corpus based on the filter given.

- route used: /getAuthors, /getWorks, /getTheso, /download-custom-search-json, /download-custom-search-csv, /customSearch
  
### Section Component

Build the header of the current work structure part (chapter title, book title etc) before display Paragraph.

- route used: /getChildren, /getConcepts, /getParagraphs, /getChildrenType, /getCurrentType

### Table of Content 

Build the table of content of the given work list structure

- route used: no fetch
- 
### Tooltip

Build tooltip of the "Explore the corpus" page

- route used: no fetch
  
### Work Component (obsolete)

To be deleted. Show text paragraph and annotation from the given URI

- route used: /getParagraphAlone, /getConcepts
