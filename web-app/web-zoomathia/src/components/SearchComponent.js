import { useState, useEffect, useRef } from "react"
import styles from "./css_modules/SearchComponent.module.css"
import AsyncSelect from 'react-select/async'
import Tooltip from "@mui/material/Tooltip"
import InfoIcon from '@mui/icons-material/Info';
import { Checkbox, FormControlLabel, IconButton } from "@mui/material"
import Grid from '@mui/material/Grid2';
import { SimpleTreeView } from '@mui/x-tree-view/SimpleTreeView';
import { styled } from '@mui/material/styles';
import Summary from "./Summary"
import DisplaySearch from "./DisplaySearch"
import Switch from '@mui/material/Switch';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';



const LOADING_STATE = <section className={styles["text-part"]}>
    <div className={styles["loader"]}></div>
    <p>Loading data...</p>
</section>

const AntSwitch = styled(Switch)(({ theme }) => ({
    width: 28,
    height: 16,
    padding: 0,
    display: 'flex',
    '&:active': {
      '& .MuiSwitch-thumb': {
        width: 15,
      },
      '& .MuiSwitch-switchBase.Mui-checked': {
        transform: 'translateX(9px)',
      },
    },
    '& .MuiSwitch-switchBase': {
      padding: 2,
      '&.Mui-checked': {
        transform: 'translateX(12px)',
        color: '#fff',
        '& + .MuiSwitch-track': {
          opacity: 1,
          backgroundColor: '#1890ff',
          ...theme.applyStyles('dark', {
            backgroundColor: '#177ddc',
          }),
        },
      },
    },
    '& .MuiSwitch-thumb': {
      boxShadow: '0 2px 4px 0 rgb(0 35 11 / 20%)',
      width: 12,
      height: 12,
      borderRadius: 6,
      transition: theme.transitions.create(['width'], {
        duration: 200,
      }),
    },
    '& .MuiSwitch-track': {
      borderRadius: 16 / 2,
      opacity: 1,
      backgroundColor: 'rgba(0,0,0,.25)',
      boxSizing: 'border-box',
      ...theme.applyStyles('dark', {
        backgroundColor: 'rgba(255,255,255,.35)',
      }),
    },
  }));

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
    const [lang, setLang] = useState('en')

    const [checked, setChecked] = useState(false)
    const [subConcepts, setSubConcepts] = useState(false)

    const [searchResult, setSearchResult] = useState([])
    const [currentWorkLoading, setCurrentWorkLoading] = useState("")

    const [summary, setSummary] = useState([])
    const [stats, setStats] = useState(null)

    const controller = useRef(new AbortController())

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

    const changeLang = async (e) => {
        setConceptList(await getConcepts(e.target.value))
        setLang(e.target.value)
        //TODO: Changer la liste des concepts présent dans l'input select
        
    }

    const sendRequestedForm = async () => {

        if(controller.current)
        console.log(checked)
        // All form empty, no search
        if(author.length === 0 && work.length === 0 && concepts.length === 0){
            console.log("Avoiding overloading: Search cancel due to no input...")
            return
        }

        setSearchResult(LOADING_STATE)
        setStats([])
        setSummary([])

        if (controller.current) {
            controller.current.abort("Canceling Fetch: Work has changed...")
        }
        controller.current = new AbortController()
        const signal = controller.current.signal

        // Requête POST
        const searchObject = JSON.stringify({
            author: author.map(e => e.value),
            work: work.map(e => e.value),
            concepts: concepts.map(e => {return{uri: e.value, type: e.type}}),
            checked: checked,
            subConcepts: subConcepts
        })
        let time1 = performance.now()
        const data_retreive = await fetch(`${process.env.REACT_APP_BACKEND_URL}customSearch`,
            {
                method: "POST",
                mode: "cors",
                headers: {
                  "Content-Type": "application/json",
                },
                body: searchObject,
                signal
              }
        ).then(response => response.json()).catch(e => {console.log(e)})
        let time2 = performance.now()

        console.log(data_retreive)
        const displaySearch = []
        if(Object.keys(data_retreive.tree).length === 0){
            displaySearch.push(<div className={styles["box-result"]}><p>No result for this custom filter</p></div>)
            setSummary([])
        }else{
            setStats(<section className={styles["selected-book-metadata"]}>
                <div className={styles["block-stat"]}>
                    <h4>Results</h4>
                    <p>Number of Work: {data_retreive.tree.length}</p>
                    <p>Request time: {(time2 - time1) / 1000} s</p>
                </div>
                <div className={styles["block-stat"]}>
                    <h4>Export SPARQL Result: </h4>
                    <div className={styles["btn-export-multiple"]}>
                        <a href={`${process.env.REACT_APP_BACKEND_URL}download-custom-search-json?sparql=${encodeURIComponent(data_retreive.sparql)}`} className={styles["btn-download"]} download target="_blank" rel="noreferrer">JSON</a>
                        <a href={`${process.env.REACT_APP_BACKEND_URL}download-custom-search-csv?sparql=${encodeURIComponent(data_retreive.sparql)}`} className={styles["btn-download"]} download target="_blank" rel="noreferrer">CSV</a>
                    </div>
                </div>
                
                
                {currentWorkLoading}
            </section>)
            setSummary(<div className={styles["ul-toc"]}>
                    <h2>Table of content</h2>
                    <ul>{data_retreive.tree !== null ? data_retreive.tree.map(node => <SimpleTreeView key={node.uri}>
                <Summary key={node.uri} node={node} currentBook={null} setChange={null} setCurrentBook={null} />
                </SimpleTreeView>
                    ) : ''}</ul>
            </div>)
            console.log(data_retreive.tree)
            for(const node of data_retreive.tree){
                displaySearch.push(<DisplaySearch node={node} controller={controller}/>)
            }
        }
        
        setCurrentWorkLoading("")
        setSearchResult(displaySearch)
    }

    const getConcepts = async (language="en") => {
        const data_concepts = await fetch(`${process.env.REACT_APP_BACKEND_URL}getTheso?lang=${language}`
        ).then(response => response.json())
            .catch(e => { console.log(e) })

        return data_concepts
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
                        <FormControl sx={{ m: 1, minWidth: 80 }}>
                        <InputLabel id="demo-simple-select-autowidth-label">Lang</InputLabel>
                        <Select
                            labelId="demo-simple-select-autowidth-label"
                            id="demo-simple-select-autowidth"
                            value={lang}
                            onChange={changeLang}
                            autoWidth
                            label="lang">
                            <MenuItem value="">
                                <em></em>
                            </MenuItem>
                            <MenuItem value="en">English</MenuItem>
                            <MenuItem value="fr">Français</MenuItem>
                            <MenuItem value="it">Italiano</MenuItem>
                        </Select>
                    </FormControl>
                    </div>
                    <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
                            <Typography>OR</Typography>
                            <AntSwitch inputProps={{ 'aria-label': 'ant design' }} onChange={e => setChecked(!checked)}/>
                            <Typography>AND</Typography>
                            <FormControlLabel className={styles["concept-checkbox"]} control={<Checkbox color="secondary" onChange={e => setSubConcepts(!subConcepts)}/>} label="Add sub-concepts" />
                    </Stack>
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
            </Grid>
        </Grid>
        
        
    </div>

}

export default SearchComponent;

/*<label>AND<input type="checkbox" onChange={e => setChecked(!checked)}/></label>*/