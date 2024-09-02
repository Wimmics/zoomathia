import { useState, useEffect } from "react"
import styles from "./css_modules/SearchComponent.module.css"
import AsyncSelect from 'react-select/async'


const SearchComponent = () => {

    // Selected value
    const [author, setAuthor] = useState([])
    const [work, setWork] = useState([])
    const [concepts, setConcepts] = useState([])
    // Options list for AsyncSelect
    const [authorList, setAuthorList] = useState([])
    const [workList, setWorkList] = useState([])
    const [conceptList, setConceptList] = useState([])
    const [checked, setChecked] = useState(false)

    const filterList = async (input, listOptions) => {
        return listOptions.filter(e => e.label.includes(input))
    }

    const authorSelect = <AsyncSelect key={"author-select"} className={styles["selection-input"]}
        placeholder="Select author(s)"
        defaultOptions={authorList}
        loadOptions={(input) => filterList(input, authorList)}
        isMulti
        onChange={(e) => setAuthor(e || [])}
    />

    const workSelect = <AsyncSelect key={"work-select"} className={styles["selection-input"]}
        placeholder="Select work(s)"
        defaultOptions={workList}
        loadOptions={(input) => filterList(input, workList)}
        isMulti
        onChange={(e) => setWork(e || [])}
    />

    const conceptsSelect = <AsyncSelect key={"concepts-select"} className={styles["selection-input"]}
        placeholder="Select concept(s)"
        defaultOptions={conceptList}
        loadOptions={(input) => filterList(input, conceptList)}
        isMulti
        onChange={(e) => setConcepts(e || [])}
    />

    const sendRequestedForm = async () => {

        // Requête POST
        const searchObject = JSON.stringify({
            author: author.map(e => e.value),
            work: work.map(e => e.value),
            concepts: concepts.map(e => {return{uri: e.value, type: e.type}}),
            checked: checked
        })

        console.log(searchObject)

        const data_retreive = await fetch(`${process.env.REACT_APP_BACKEND_URL}customSearch`,
            {
                method: "POST",
                mode: "cors",
                headers: {
                  "Content-Type": "application/json",
                },
                body: searchObject
              }
        ).then(response => response.json()).catch(e => {console.log(e)})
        console.log(data_retreive)

        
    }

    useEffect(() => {
        const getAuthors = async () => {
            const author_response = []

            const data_author = await fetch(`${process.env.REACT_APP_BACKEND_URL}getAuthors`
            ).then(response => response.json()).catch(e => { console.log(e) })
            for (const author of data_author) {
                author_response.push({ value: author.name, label: author.name })
            }
    
            return author_response
        }
    
        const getWorks = async () => {
            const work_response = []

            const data_works = await fetch(`${process.env.REACT_APP_BACKEND_URL}getWorks`
            ).then(response => response.json())
                .catch(e => { console.log(e) })
            for (const work of data_works) {
                work_response.push({ value: work.uri, label: work.title, author: work.author })
            }
    
            return work_response
        }

        const getConcepts = async () => {
            const concept_response = []

            const data_concepts = await fetch(`${process.env.REACT_APP_BACKEND_URL}getTheso`
            ).then(response => response.json())
                .catch(e => { console.log(e) })
    
            return data_concepts
        }

        const loadData = async () => {
            setAuthorList( await getAuthors())
            setWorkList( await getWorks())
            setConceptList(await getConcepts())
        }
        loadData()
    }, [])

    return <div className={styles["box-content"]}>
        <section className={styles["section-form"]}>
            <h2>Set a custom filter</h2>
            <p>This formulary can take multiple value per input. The default behaviour for author(s) and work(s) input is an "OR" value and cannot be change.</p>
            <p>For the select concept(s) input, a checkbox specify if the search strategy should be an OR value or an AND value.</p>
            <div className={styles["block-input"]}>
                <div className={styles["search-input"]}>
                    <label>Filter on author(s):</label>
                    {authorSelect}
                </div>
                <div className={styles["search-input"]}>
                    <label>Filter on work(s):</label>
                    {workSelect}
                </div>
                <div className={styles["search-input"]}>
                    <label>Filter on concept(s):</label>
                    {conceptsSelect}
                    <label>AND<input type="checkbox" onChange={e => setChecked(!checked)}/></label>
                </div>
            </div>
            <button className={styles["btn-submit-search"]} onClick={sendRequestedForm}>search</button>
        </section>
    </div>

}

export default SearchComponent;