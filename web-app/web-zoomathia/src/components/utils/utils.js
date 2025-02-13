const executeSPARQLRequest = async (endpoint, query) => {
    localStorage.clear()
    const url = `${endpoint}?query=${encodeURIComponent(query)}&format=json`;

    let result_data = await fetch(url, {
        mode: 'cors',
        headers: {
            'Content-Type': 'text/plain',
            'Accept': "application/sparql-results+json"
        }
    })
    //console.log(JSON.stringify(await result_data.text()))
    return await result_data.json()
}

const queryFetch = (entpoint, query) => {

}

export { executeSPARQLRequest }