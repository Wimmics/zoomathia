import { useState, useEffect } from "react"
import styles from "./css_modules/SearchComponent.module.css"
import AsyncSelect from 'react-select/async'
import ParagraphDisplay from "./ParagraphComponent"
import Tooltip from "@mui/material/Tooltip"
import InfoIcon from '@mui/icons-material/Info';
import { IconButton } from "@mui/material"
import Grid from '@mui/material/Grid2';
import { SimpleTreeView } from '@mui/x-tree-view/SimpleTreeView';
import { TreeItem } from '@mui/x-tree-view/TreeItem';
import Summary from "./Summary"
import DisplaySearch from "./DisplaySearch"



const LOADING_STATE = <section className={styles["text-part"]}>
    <div className={styles["loader"]}></div>
    <p>Loading data...</p>
</section>

const logicConceptTooltip = "For the search concept(s) field, the checkbox specify if the search strategy should be an OR value logic or an AND value logic."

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
    const [searchResult, setSearchResult] = useState([])
    const [currentWorkLoading, setCurrentWorkLoading] = useState("")
    const [summary, setSummary] = useState([])
    const [stats, setStats] = useState(null)

    const filterList = async (input, listOptions) => {
        return listOptions.filter(e => e.label.toLowerCase().includes(input.toLowerCase()))
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

        // All form empty, no search
        if(author.length === 0 && work.length === 0 && concepts.length === 0){
            console.log("Avoiding overloading: Search cancel due to no input...")
            return
        }

        setSearchResult(LOADING_STATE)

        // Requête POST
        const searchObject = JSON.stringify({
            author: author.map(e => e.value),
            work: work.map(e => e.value),
            concepts: concepts.map(e => {return{uri: e.value, type: e.type}}),
            checked: checked
        })

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
        const displaySearch = []
        if(Object.keys(data_retreive).length === 0){
            displaySearch.push(<div className={styles["box-result"]}><p>No result for this custom filter</p></div>)
        }else{
            setStats(<section className={styles["selected-book-metadata"]}>
                <h4>Resultat</h4>
                <p>Number of Work: {data_retreive.length}</p>
            </section>)
            setSummary(<div className={styles["ul-toc"]}>
                    <h2>Table of content</h2>
                    <ul>{data_retreive !== null ? data_retreive.map(node => <SimpleTreeView key={node.uri}>
                <Summary key={node.uri} node={node} currentBook={() => <></>} setChange={() => <></>} setCurrentBook={() => <></>} />
                </SimpleTreeView>
                    ) : ''}</ul>
            </div>)

            for(const node of data_retreive){
                console.log("Yes")
                displaySearch.push(<DisplaySearch node={node}/>)
            }
        }
        
        setCurrentWorkLoading("")
        setSearchResult(displaySearch)
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
            <h2>Define a custom filter</h2>
            <p><u>Note:</u> This form can take multiple values for each search field. The default the result is union between values of the author and the work search field.</p>
            <div className={styles["block-input"]}>
                <div className={styles["search-input"]}>
                    <label>Filter on author(s):</label>
                    {authorSelect}
                </div>
                <div className={styles["search-input"]}>
                    <label>Filter on work(s):</label>
                    {workSelect}
                </div>
                <div className={styles["search-input-border"]}>
                    <label>Filter on concept(s):<Tooltip title={logicConceptTooltip}><IconButton><InfoIcon /></IconButton></Tooltip></label>
                    <div className={styles["search-concept"]}>
                        {conceptsSelect}
                        <label>AND<input type="checkbox" onChange={e => setChecked(!checked)}/></label>
                    </div>
                </div>
                <button className={styles["btn-submit-search"]} onClick={sendRequestedForm}>Search</button>
            </div>
            
        </section>
        <Grid container spacing={2}>
            <Grid size={12}>
                {stats}
            </Grid>
            <Grid size={2}>
                {summary}
            </Grid>
            <Grid size={10}>
            {searchResult}
            {currentWorkLoading}
            </Grid>
        </Grid>
        
        
    </div>

}

export default SearchComponent;