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

const getMetadata = (uri) => {
  return `prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  SELECT DISTINCT ?author ?editor ?file ?date WHERE {
    <${uri}> a zoo:Oeuvre;
      zoo:author ?author;
      zoo:date ?date;
      zoo:editor ?editor.
      Optional {
        <${uri}> zoo:file ?file_t.
      }
      BIND(IF(BOUND(?file_t), ?file_t, 'word_files') as ?file)
  }`
}

router.get("/getMetadata", async (req, res) => {
  console.log(req.query.uri)
  const result = await executeSPARQLRequest(endpoint, getMetadata(req.query.uri))
  let response = {}
  for (const elt of result.results.bindings) {
    response = {
      author: elt.author.value,
      editor: elt.editor.value,
      date: elt.date.value,
      file: elt.file.value
    }
  }

  res.status(200).json(response)
})

/*
{
      <${uri}> a zoo:Oeuvre;
          zoo:identifier ?id;
          zoo:title ?title;
    BIND(zoo:Oeuvre as ?type)
    BIND(<${uri}> as ?current)
    }UNION{
      ?current a ?type;
          zoo:isPartOf+ <${uri}>;
          zoo:isPartOf ?parent_t;
          zoo:identifier ?id.
        BIND(IF(?parent = <${uri}>, ?current, ?parent_t) AS ?parent)
      Optional {
        ?current zoo:title ?title_t.
      }
      BIND(IF(BOUND(?title_t), ?title_t, "") AS ?title)
    }
}ORDER BY ?parent ?id`
*/

const getSummary = (uri) => {
  return `prefix zoo:     <http://www.zoomathia.com/2024/zoo#>
SELECT DISTINCT ?parent ?current ?type (xsd:integer(?id_t) as ?id) ?title ?file WHERE {
      ?current a ?type;
          zoo:isPartOf+ <${uri}>;
          zoo:isPartOf ?parent_t;
          zoo:identifier ?id_t.
        BIND(IF(?parent_t = <${uri}>, ?current, ?parent_t) AS ?parent)
      Optional {
        ?current zoo:title ?title_t.
      }
      BIND(IF(BOUND(?title_t), ?title_t, "") AS ?title)
}ORDER BY ?id ?parent`
}

router.get("/getSummary", async (req, res) => {
  const result = await executeSPARQLRequest(endpoint, getSummary(req.query.uri))
  const tree = []
  const response = {}
  const idInSet = new Set()

  for (const elt of result.results.bindings) {
    response[elt.current.value] = {
      uri: elt.current.value,
      id: elt.id.value,
      title: elt.title.value,
      type: elt.type.value,
      children: []
    }
  }

  for (const elt of result.results.bindings) {
    if ((elt.current.value === elt.parent.value) && (!idInSet.has(elt.current.value))) {
      tree.push(response[elt.current.value])
      idInSet.add(elt.current.value)
    } else {
      response[elt.parent.value].children.push(response[elt.current.value])
    }
  }

  try {
    res.status(200).json(tree)
  } catch (e) {
    console.log(tree)
    res.status(200).end(JSON.stringify(tree))
  }

})

const getWorkPart = (title) => {
  return `prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  SELECT DISTINCT ?part ?type ?id ?title WHERE {
    ?part a ?type;
      zoo:identifier ?id;
      zoo:title ?title.
    
    <${title}> zoo:hasPart ?part.
  }ORDER BY ?id`
}

router.get('/getWorkPart', async (req, res) => {
  const result = await executeSPARQLRequest(endpoint, getWorkPart(req.query.title))
  let response = []
  console.log(req.query.title)

  for (const elt of result["results"]["bindings"]) {
    response.push({
      uri: elt["part"]["value"],
      id: elt["id"]["value"],
      title: elt["title"]["value"],
      type: elt['type'].value
    })
  }

  res.status(200).json(response);
});

const getAuthors = () => {
  return `prefix schema: <http://schema.org/>
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  SELECT DISTINCT ?name WHERE {
    ?oeuvre (schema:author|zoo:author) ?name
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
  console.log(author)
  return `prefix schema: <http://schema.org/>
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#>

  SELECT ?oeuvre ?title WHERE {
    ?oeuvre (zoo:author|schema:author) ?author;
    (schema:title|zoo:title) ?title.

    filter(str(?author) = "${author}")
  }ORDER BY ?title`
}

router.get('/getWorksFromAuthors', async (req, res) => {
  console.log("Get works from author")
  const response = []
  const result = await executeSPARQLRequest(endpoint, getWorksFromAuthor(req.query.author))
  for (const elt of result.results.bindings) {
    response.push({
      uri: elt.oeuvre.value,
      title: elt.title.value,
      author: req.query.author
    })
  }
  res.status(200).json(response)
})

const getWorks = () => {
  return `prefix schema: <http://schema.org/>
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#>

  SELECT ?oeuvre ?title ?author WHERE {
    ?oeuvre (zoo:author|schema:author) ?author;
    (schema:title|zoo:title) ?title.
  }ORDER BY ?title`
}

router.get('/getWorks', async (req, res) => {
  console.log("Get works from author")
  const response = []
  const result = await executeSPARQLRequest(endpoint, getWorks())
  for (const elt of result.results.bindings) {
    response.push({
      uri: elt.oeuvre.value,
      title: elt.title.value,
      author: elt.author.value
    })
  }
  res.status(200).json(response)
})

const getChildrenTypeQuery = (uri) => {
  return `prefix schema: <http://schema.org/>
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  SELECT DISTINCT ?childType WHERE {
    <${uri}> zoo:hasPart ?child.
  
    ?child a ?childType;
  }`
}

router.get("/getChildrenType", async (req, res) => {
  console.log(req.query.uri)
  const response = []
  const result = await executeSPARQLRequest(endpoint, getChildrenTypeQuery(req.query.uri))

  for (const elt of result.results.bindings) {
    response.push(elt["childType"].value)
  }

  res.status(200).json(response)
})

const getChildrenQuery = (uri) => {
  return `prefix schema: <http://schema.org/>
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  SELECT DISTINCT ?child ?identifier ?title ?type WHERE {
    <${uri}> zoo:hasPart ?child.
    ?child a ?type;
 	zoo:identifier ?identifier.
    OPTIONAL {
      ?child zoo:title ?titleprov.
    }
    BIND(IF(BOUND(?titleprov), ?titleprov, ?identifier) AS ?title)
  }ORDER BY ?identifier`
}

router.get("/getChildren", async (req, res) => {
  const response = []
  const result = await executeSPARQLRequest(endpoint, getChildrenQuery(req.query.uri))

  for (const elt of result.results.bindings) {
    response.push({
      uri: elt.child.value,
      title: elt.title.value,
      type: elt.type.value
    })
  }

  res.status(200).json(response)
})

const getParagraphQuery = (uri) => {
  return `prefix schema: <http://schema.org/>
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  SELECT DISTINCT (xsd:integer(?id_p) as ?id) ?title ?uri ?text WHERE {
    <${uri}> zoo:title ?title.

    ?uri a zoo:Paragraph;
      zoo:isPartOf <${uri}>;
      zoo:identifier ?id_p;
      zoo:text ?text.
}ORDER BY ?id`
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

const getCurrentType = (uri) => {
  return `prefix schema: <http://schema.org/>
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  SELECT DISTINCT ?type WHERE {
    <${uri}> a ?type
    }`
}

router.get("/getCurrentType", async (req, res) => {
  console.log(`Get type of ${req.query.uri}`)
  const response = []
  const result = await executeSPARQLRequest(endpoint, getCurrentType(req.query.uri));
  for (const elt of result.results.bindings) {
    response.push({ type: elt.type.value })
  }
  res.status(200).json(response)
})

const getParagraphAloneQuery = (uri) => {
  return `prefix schema: <http://schema.org/>
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  SELECT DISTINCT ?paragraph (xsd:integer(?id_p) as ?id) ?text WHERE {
    ?oeuvre zoo:hasPart+ ?parent
  ?parent zoo:hasPart ?paragraph
  ?paragraph zoo:text ?text;
  	zoo:identifier ?id_p.
  FILTER EXISTS {
    ?parent zoo:hasPart <${uri}>
  }
}order by ?id`
}

router.get('/getParagraphAlone', async (req, res) => {
  let response = []
  const result = await executeSPARQLRequest(endpoint, getParagraphAloneQuery(req.query.uri));
  console.log(result.results.bindings)
  for (const elt of result.results.bindings) {
    response.push({
      uri: elt.paragraph.value,
      text: elt.text.value,
      id: elt.id.value
    })
  }

  res.status(200).json(response)
})

const getConceptsQuery = (uri, lang) => {
  return `prefix schema: <http://schema.org/>
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  prefix oa: <http://www.w3.org/ns/oa#>
  prefix skos:    <http://www.w3.org/2004/02/skos/core#> 
  SELECT DISTINCT ?annotation ?concept ?label ?start ?end ?exact WHERE {
    ?annotation oa:hasBody ?concept;
      oa:hasTarget [
        oa:hasSource <${uri}>;
        oa:hasSelector ?selector
      ].
    ?selector oa:exact ?exact
  
  ?concept skos:prefLabel ?labelen
  FILTER(lang(?labelen) = "en")
  OPTIONAL {
    ?concept skos:prefLabel ?labellang
    FILTER(lang(?labellang) = "${lang}")
  }
  OPTIONAL {
    ?selector oa:start ?start;
      oa:end ?end
  }
  BIND(IF(BOUND(?labellang), ?labellang, ?labelen) AS ?label)
  
  }ORDER BY ?label`
}

router.get('/getConcepts', async (req, res) => {
  const result = await executeSPARQLRequest(endpoint, getConceptsQuery(req.query.uri, req.query.lang))
  const response = []

  for (const elt of result.results.bindings) {
    response.push({
      annotation: elt.annotation.value,
      concept: elt.concept.value,
      label: elt.label.value,
      start: elt.start ? parseInt(elt.start.value) : 0,
      end: elt.end ? parseInt(elt.end.value) : 0,
      exact: elt.exact.value
    })
  }

  res.status(200).json(response)
})

const searchConceptsQuery = (input, lang) => {
  return `prefix schema: <http://schema.org/>
  prefix oa: <http://www.w3.org/ns/oa#>
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
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
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  SELECT DISTINCT ?paragraph ?title ?id ?text WHERE {
    <${uri}> schema:title ?title.

    ?paragraph zoo:text ?text;
      zoo:identifier ?id;
      zoo:isPartOf <${uri}>.

    ${subpart}
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
  prefix zoo:     <http://www.zoomathia.com/2024/zoo#> 
  SELECT DISTINCT ?uri ?author ?title ?book ?paragraph (xsd:integer(?id_p) as ?id) ?text WHERE {
    ${subpart}
    ?paragraph zoo:text ?text;
      zoo:identifier ?id_p;
      zoo:isPartOf ?uri.
    
    ?uri zoo:identifier ?book;
      zoo:title ?title.

    ?oeuvre zoo:author ?author;
      zoo:hasPart+ ?uri.
    
    ?concept skos:prefLabel ?label

    FILTER(lang(?label) = "en")
  }ORDER BY ?book ?id
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
      bookId: elt.book.value,
      title: elt.title.value,
      uri: elt.paragraph.value,
      text: elt.text.value,
      id: elt.id.value
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
  console.log("Recieved query for QC ", req.query.id)
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
    spo: fs.readFileSync(`queries/qc${req.query.id}_spo.rq`, 'utf8'),
    table: {
      columns: result.head.vars,
      data: data
    }
  }
  return res.status(200).json(response)
})

module.exports = router;
