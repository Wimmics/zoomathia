let fs = require('fs');

const executeDescribeRequest = async (endpoint, query) => {
    const url = `${endpoint}?query=${encodeURIComponent(query)}&format=turtle`;

    /**
     * TODO:  Catch unexpected error during fetch (fetchControler)
     */
    try {
        let result_data = await fetch(url, {
            headers: {
                'Content-Type': 'text/plain',
                'Accept': `text/turtle`
            }
        })
        return await result_data.text()
    }
    catch (e) {
        console.log(`Request fail...`)
        console.log(e)
        if (e.cause?.code === 'ECONNREFUSED') {
            console.log("SPARQL Endpoint unreachable, server is not launch or doesn't accept connection")
        } else {
            console.log(e.cause)
        }
        return "Doesn't work..."
    }
}

const executeSPARQLRequest = async (endpoint, query) => {
    const url = `${endpoint}?query=${encodeURIComponent(query)}&format=json`;

    /**
     * TODO:  Catch unexpected error during fetch (fetchControler)
     */
    try {
        let result_data = await fetch(url, {
            headers: {
                'Content-Type': 'text/plain',
                'Accept': `application/sparql-results+json`
            }
        })
        return await result_data.json()
    }
    catch (e) {
        console.log(`Request fail...`)
        console.log(e)
        if (e.cause?.code === 'ECONNREFUSED') {
            console.log("SPARQL Endpoint unreachable, server is not launch or doesn't accept connection")
        } else {
            console.log(e.cause)
        }
        return {
            results: {
                bindings: []
            }
        }
    }
}

/**
 * Read a SPARQL query template and replace the {id} placeholder
 * @param {string} template - the template file name
 * @param {number} id - value to replace "{id}" with
 * @returns {string} SPARQL query string
 */
const readTemplate = (template, id) => {
    let queryTpl = fs.readFileSync('queries/' + template, 'utf8');
    return queryTpl.replaceAll("{id}", id);
}

/**
 * Read a SPARQL query template and replace the {id} placeholder
 * @param {string} template - the template file name
 * @param {number} id - value to replace "{id}" with
 * @returns {string} SPARQL query string
 */
const getCompetenciesQuestion = (file) => {
    let queryTpl = fs.readFileSync(`queries/qc${file}.rq`, 'utf8');
    return queryTpl;
}

const checkParagraph = (node, paragraph) => {
    for(const p of node.children){
        if(p.id === paragraph.id){
            return true
        }
    }
    return false
}

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const jsonToCsv = (jsonObject) => {
    const header = jsonObject.head.vars
    let fileWriter = []

    fileWriter.push(header.join(";"))

    for(const line of jsonObject.results.bindings){
        const temp = []
        for(const title of header){
            temp.push(line[title].value)
        }
        fileWriter.push(temp.join(";"))
    }

    return fileWriter.join("\n")
}

exports.executeSPARQLRequest = executeSPARQLRequest;
exports.readTemplate = readTemplate;
exports.getCompetenciesQuestion = getCompetenciesQuestion;
exports.checkParagraph = checkParagraph;
exports.executeDescribeRequest = executeDescribeRequest;
exports.getTypeFromURI = getTypeFromURI;
exports.jsonToCsv = jsonToCsv;