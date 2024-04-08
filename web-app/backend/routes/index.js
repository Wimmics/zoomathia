let { executeSPARQLRequest, readTemplate, getCompetenciesQuestion } = require('./utils.js')
let express = require('express');
const { qcs } = require("../queries/qcs.js")
const axios = require('axios');
const fs = require("fs")
let router = express.Router();

const endpoint = "http://localhost:8080/sparql"

/* GET home page. */
router.get('/', async (req, res) => {
  res.status(200);
});

const getBookList = (title) => {
  return `prefix schema: <http://schema.org/>
  SELECT ?book ?id WHERE {
    ?book a schema:Book;
      schema:identifier ?id.
    
    <${title}> schema:hasPart ?book.
  }`
}

router.get('/getBookList', async (req, res) => {
  const result = await executeSPARQLRequest(endpoint, getBookList(req.query.title))
  let response = []

  for (const elt of result["results"]["bindings"]) {
    response.push({
      uri: elt["book"]["value"],
      id: parseInt(elt["id"]["value"])
    })
  }

  response = response.sort((a, b) => {
    if (a.id > b.id) {
      return 1
    }
    if (a.id < b.id) {
      return -1
    }
    return 0
  })

  res.status(200).json(response);
});

const getParagraphWithConcept = (input, uri) => {
  return `prefix schema: <http://schema.org/>
  prefix oa: <http://www.w3.org/ns/oa#>
  SELECT DISTINCT ?paragraph ?title ?id ?text WHERE {
    ?annotation oa:hasBody ?concept;
      oa:hasTarget [
        oa:hasSource ?paragraph
      ].

    ?paragraph schema:text ?text;
      schema:identifier ?id;
      schema:isPartOf <${uri}>.

    <${uri}> schema:title ?title.
    
    ?concept skos:prefLabel ?label

    FILTER(lang(?label) = "en")
    FILTER(str(?label) = "${input}")
  }
  `
}

const getParagraphsWithConcept = (input) => {
  return `prefix schema: <http://schema.org/>
  prefix oa: <http://www.w3.org/ns/oa#>
  SELECT DISTINCT ?uri ?author ?title (xsd:integer(?book) as ?bookid) ?paragraph (xsd:integer(?id) as ?nb) ?text WHERE {
    ?annotation oa:hasBody ?concept;
      oa:hasTarget [
        oa:hasSource ?paragraph
      ].

    ?paragraph schema:text ?text;
      schema:identifier ?id;
      schema:isPartOf ?uri.
    
    ?uri schema:identifier ?book;
      schema:title ?title.

    ?oeuvre schema:author ?author;
      schema:hasPart ?uri.
    
    ?concept skos:prefLabel ?label

    FILTER(lang(?label) = "en")
    FILTER(str(?label) = "${input}")
  }ORDER BY ?bookid ?nb
  `
}

const getAuthors = () => {
  return `prefix schema: <http://schema.org/>
  SELECT ?name WHERE {
    ?oeuvre schema:author ?name
  }ORDER BY ?name
`
}

router.get('/getAuthors', async (req, res) => {
  console.log("Get author")
  const response = []
  const result = await executeSPARQLRequest(endpoint, getAuthors());
  for (const author of result.results.bindings) {
    response.push({ name: author.name.value })
  }
  res.status(200).json(response)
})

const getWorksFromAuthor = (author) => {
  return `prefix schema: <http://schema.org/>
  SELECT ?oeuvre ?title WHERE {
    ?oeuvre schema:author ?author;
      schema:title ?title.
    filter(str(?author) = "${author}")
  }ORDER BY ?title
  `
}

router.get('/getWorks', async (req, res) => {
  console.log("Get works from author")
  const response = []
  const result = await executeSPARQLRequest(endpoint, getWorksFromAuthor(req.query.author))
  for (const elt of result.results.bindings) {
    response.push({
      uri: elt.oeuvre.value,
      title: elt.title.value
    })
  }
  res.status(200).json(response)
})

const getParagraphQuery = (uri) => {
  return `prefix schema: <http://schema.org/>
  SELECT (xsd:integer(?id_p) as ?id) ?title ?uri ?text WHERE {
    ?uri schema:isPartOf <${uri}>;
      schema:identifier ?id_p;
      schema:text ?text
    <${uri}> schema:title ?title.
}
ORDER BY ?id`
}

router.get('/getParagraphs', async (req, res) => {
  console.log(`Get paragraphs for ${req.query.uri}`)
  let response = []
  const result = await executeSPARQLRequest(endpoint, getParagraphQuery(req.query.uri));
  for (const elt of result.results.bindings) {
    response.push({
      title: elt.title.value,
      uri: elt.uri.value,
      text: elt.text.value,
      id: elt.id.value
    })
  }

  res.status(200).json(response)
})

const getConceptsQuery = (uri, lang) => {
  return `prefix schema: <http://schema.org/>
  prefix oa: <http://www.w3.org/ns/oa#>
  SELECT DISTINCT ?annotation ?concept ?label ?start ?end ?exact WHERE {
    ?annotation oa:hasBody ?concept;
      oa:hasTarget [
        oa:hasSource <${uri}>;
        oa:hasSelector [
          oa:start ?start;
          oa:end ?end;
          oa:exact ?exact
        ]
      ].
  
  ?concept skos:prefLabel ?labelen
  FILTER(lang(?labelen) = "en")
  OPTIONAL {
    ?concept skos:prefLabel ?labellang
    FILTER(lang(?labellang) = "${lang}")
  }
  BIND(IF(BOUND(?labellang), ?labellang, ?labelen) AS ?label)
  
  }`
}

router.get('/getConcepts', async (req, res) => {
  const result = await executeSPARQLRequest(endpoint, getConceptsQuery(req.query.uri, req.query.lang))
  const response = []
  console.log(req.query.lang)
  for (const elt of result.results.bindings) {
    response.push({
      annotation: elt.annotation.value,
      concept: elt.concept.value,
      label: elt.label.value,
      start: parseInt(elt.start.value),
      end: parseInt(elt.end.value),
      exact: elt.exact.value
    })
  }

  res.status(200).json(response)
})

const searchConceptsQuery = (input, lang) => {
  return `prefix schema: <http://schema.org/>
  prefix oa: <http://www.w3.org/ns/oa#>
  SELECT DISTINCT ?concept ?label WHERE {
    ?concept skos:prefLabel ?label
    FILTER(lang(?label) = "${lang}")
    FILTER(contains(str(?label), "${input}"))
  }`
}

router.get('/searchConcepts', async (req, res) => {
  console.log(`Search concept query for input: ${req.query.input}`)
  const result = await executeSPARQLRequest(endpoint, searchConceptsQuery(req.query.input, req.query.lang))
  const response = []

  for (const elt of result.results.bindings) {
    response.push({
      uri: elt.concept.value,
      label: elt.label.value
    })
  }

  res.status(200).json(response)
})

const buildAnnotation = (labels) => {
  const query = []
  for (let i = 0; i < labels.length; i++) {
    query.push(
      `?annotation${i} oa:hasBody <${labels[i].value}>;
      oa:hasTarget [
        oa:hasSource ?paragraph;
      ].
      `)
  }
  return query.join('\n')
}

const getParagraphsWithConcepts = (subpart, uri) => {
  return `prefix schema: <http://schema.org/>
  prefix oa: <http://www.w3.org/ns/oa#>
  SELECT DISTINCT ?paragraph ?title (xsd:integer(?id_p) as ?id) ?text WHERE {
    ${subpart}
    ?paragraph schema:text ?text;
      schema:identifier ?id_p;
      schema:isPartOf <${uri}>.

    <${uri}> schema:title ?title.
  }ORDER BY ?id
  `
}

router.post('/getParagraphWithConcept', async (req, res) => {
  const result = await executeSPARQLRequest(endpoint, getParagraphsWithConcepts(buildAnnotation(req.body.concepts), req.body.uri))
  let response = []
  for (const elt of result.results.bindings) {
    response.push({
      uri: elt.paragraph.value,
      text: elt.text.value,
      title: elt.title.value,
      id: elt.id.value
    })
  }
  res.status(200).json(response)
})

const getAllParagraphsWithConcepts = (subpart) => {
  return `prefix schema: <http://schema.org/>
  prefix oa: <http://www.w3.org/ns/oa#>
  SELECT DISTINCT ?uri ?author ?title (xsd:integer(?book) as ?bookid) ?paragraph (xsd:integer(?id) as ?nb) ?text WHERE {
    ${subpart}
    ?paragraph schema:text ?text;
      schema:identifier ?id;
      schema:isPartOf ?uri.
    
    ?uri schema:identifier ?book;
      schema:title ?title.

    ?oeuvre schema:author ?author;
      schema:hasPart ?uri.
    
    ?concept skos:prefLabel ?label

    FILTER(lang(?label) = "en")
  }ORDER BY ?bookid ?nb
  `
}

router.post('/getParagraphsWithConcepts', async (req, res) => {
  const result = await executeSPARQLRequest(endpoint, getAllParagraphsWithConcepts(buildAnnotation(req.body.concepts)))
  let response = []
  //?uri ?book ?paragraph ?id ?text
  for (const elt of result.results.bindings) {
    response.push({
      author: elt.author.value,
      bookUri: elt.uri.value,
      bookId: parseInt(elt.bookid.value),
      title: elt.title.value,
      uri: elt.paragraph.value,
      text: elt.text.value,
      id: parseInt(elt.nb.value)
    })
  }
  res.status(200).json(response)
})

/**
 * Template of SPARQL query that get all available lang labels in the thesaurus
 * @returns SPARQLRequest
 */
const getLang = () => {
  return `PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
  prefix schema: <http://schema.org/>
  prefix oa: <http://www.w3.org/ns/oa#>
  SELECT DISTINCT (lang(?label) as ?lang) WHERE {
    ?concept skos:prefLabel ?label
  }`
}

/**
 * Get all available lang labels list and feed options for a select tag
 * @return {JSONObject} - output shape example:
 * [
 *    {value: "en"},
 *    {value: "fr"},
 *    {value: "lat"} 
 *    ...
 * ]
 */
router.get('/getLanguageConcept', async (req, res) => {
  const result = await executeSPARQLRequest(endpoint, getLang())
  const response = []
  for (const elt of result.results.bindings) {
    response.push({
      value: elt.lang.value
    })
  }
  res.status(200).json(response)
})

router.get("/qcList", (req, res) => {
  console.log(qcs)
  res.status(200).json(qcs)
})

/**
 * 
 */
router.get("/getQC", async (req, res) => {
  const query = getCompetenciesQuestion(`${req.query.id}`)
  const result = await executeSPARQLRequest(endpoint, query)
  const data = []
  for (const row of result.results.bindings) {
    const temp_row = []
    for (const variable of result.head.vars) {
      temp_row.push(row[variable]["value"])
    }
    data.push(temp_row)
  }

  const response = {
    query: query,
    results: result,
    table: {
      columns: result.head.vars,
      data: data
    }
  }
  return res.status(200).json(response)
})

module.exports = router;
