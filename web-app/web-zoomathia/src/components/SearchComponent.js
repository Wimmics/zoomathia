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
            for(const key of Object.keys(data_retreive)){
                const title = data_retreive[key].title
                const author = data_retreive[key].author
    
                const paragraphs = []
                for(const paragraph of data_retreive[key].paragraph){
                    setCurrentWorkLoading(<p>Loading: {paragraph.uri}</p>)
                    const concepts_list = await fetch(`${process.env.REACT_APP_BACKEND_URL}getConcepts?uri=${paragraph.uri}&lang=${"en"}`
                        ).then(response => response.json())
    
                    paragraphs.push(<ParagraphDisplay
                        key={paragraph.id}
                        id={paragraph.id}
                        text={paragraph.text}
                        uri={paragraph.uri}
                        lang={"en"}
                        concepts={concepts_list}
                        controller={null} />
                    )
                }
                displaySearch.push(<div className={styles["box-result"]}>
                    <h2>{author} - {title}</h2>
                    {paragraphs}
                </div>)
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
            <Grid size={2}>
                <h2>Table of content</h2>
                <SimpleTreeView>
                    <TreeItem itemId="grid" label="Work 1">
                        <TreeItem itemId="grid-community" label="Book 1" />
                        <TreeItem itemId="grid-pro" label="Book 2" />
                        <TreeItem itemId="grid-level-sub" label="Book 3">
                            <TreeItem itemId="Yes" label="Chapter 1"></TreeItem>
                        </TreeItem>
                        <TreeItem itemId="grid-premium" label="Book 4" />
                    </TreeItem>
                    <TreeItem itemId="pickers" label="Work 2">
                        <TreeItem itemId="pickers-community" label="@mui/x-date-pickers" />
                        <TreeItem itemId="pickers-pro" label="@mui/x-date-pickers-pro" />
                    </TreeItem>
                    <TreeItem itemId="charts" label="Work 3">
                        <TreeItem itemId="charts-community" label="@mui/x-charts" />
                    </TreeItem>
                    <TreeItem itemId="tree-view" label="Work 4">
                        <TreeItem itemId="tree-view-community" label="@mui/x-tree-view" />
                    </TreeItem>
                </SimpleTreeView>
            </Grid>
            <Grid size={10}>
                <h2>Author - Name of Work</h2>
                <Grid>
                    <h3>Chapter 1</h3>
                    <Grid>
                        
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
        {searchResult}
        {currentWorkLoading}
    </div>

}

export default SearchComponent;