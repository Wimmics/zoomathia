let fs = require('fs');

const executeSPARQLRequest = async (endpoint, query) => {
    const url = `${endpoint}?query=${encodeURIComponent(query)}&format=json`;

    /**
     * TODO:  Catch unexpected error during fetch (fetchControler)
     */

    let result_data = await fetch(url, {
        headers: {
            'Content-Type': 'text/plain',
            'Accept': "application/sparql-results+json"
        }
    })
    return await result_data.json()
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

exports.executeSPARQLRequest = executeSPARQLRequest;
exports.readTemplate = readTemplate;
exports.getCompetenciesQuestion = getCompetenciesQuestion;