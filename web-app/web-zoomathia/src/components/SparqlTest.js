import { useEffect, useState } from 'react';
import { Parser as sp } from 'sparqljs'

const SparqlTest = () => {
    const [sparqlParsed, setSparqlParsed] = useState([])

    useEffect(() => {
        let parser = new sp({ skipValidation: true });
        let parsedQuery = parser.parse(
            `SELECT * WHERE {?s ?p ?o}`
        );
        console.log(parsedQuery)
        setSparqlParsed(<p>parsedQuery</p>)
    }, [])

    return <div>
        {sparqlParsed}
    </div>
}

export default SparqlTest;