import { useState, useEffect, useCallback, useMemo } from "react"
import "gridjs/dist/theme/mermaid.min.css";
import styles from "./css_modules/CompetencyQuestionComponent.module.css"

import { Grid } from "gridjs-react"
import { html } from 'gridjs'
import Select from 'react-select'
import ExportMenu from "./ExportMenu"
import "@wimmics/venus"

const LOADING_STATE = <>
    <div className={styles["loader"]}></div>
    <p>Loading data...</p>
</>

const CompetencyQuestionComponent = () => {
    const styleGrid = useMemo(
        () => {
        return { td: {
            'text-overflow': 'ellipsis',
            'overflow': 'hidden',
            'white-space': 'normal'
        }}
    }, [])

    const [options, setOptions] = useState([])
    const [selectedQuestion, setSelectedQuestion] = useState(null)
    const [iframe, setIframe] = useState(<></>)
    const [table, setTable] = useState(
    <div className={styles["empty-state"]}>
        <p className={styles["empty-state-title"]}>No question selected</p>
        <p className={styles["empty-state-subtitle"]}>Select a competency question above to see the results</p>
    </div>
)
    const [titleVizu, setTitleVizu] = useState('')

    const updateTable = useCallback((e) => {
        setSelectedQuestion(e)
        const file = e.value
        setTable(LOADING_STATE)
        setIframe(LOADING_STATE)

        const callForData = async () => {
            const generatedCol = []
            if (file === null) { return }
            const spo_data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getQCspo?id=${file}`).then(response => response.json())
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getQC?id=${file}`).then(response => response.json())

            for (const elt of data.table.columns) {
                switch(elt){
                    case "paragraph":
                        generatedCol.push({
                            name: elt,
                            formatter: (cell) => {
                                return html(`<a href='${process.env.REACT_APP_FRONTEND_URL}ExploreAWork?uri=${cell}' target='_blank'>${cell.replace("http://www.zoomathia.com/", '')}</a>`) }
                        })
                        break;
                    case "name_anthroponym":
                        generatedCol.push({
                            name: html(`<span class="${styles["anthroponym-variable"]}">${elt}</span>`),
                        })
                        break;
                    case "name_animal":
                        generatedCol.push({
                            name: html(`<span class="${styles["animal-variable"]}">${elt}</span>`),
                        })
                        break;
                    case "animal_name":
                        generatedCol.push({
                            name: html(`<span class="${styles["animal-variable"]}">${elt}</span>`),
                        })
                        break;
                    default:
                        if(elt.includes("mention")){
                            generatedCol.push(elt)
                        }else{
                            generatedCol.push({
                                name: html(`<span class="${styles["other-variable"]}">${elt}</span>`),
                            })
                        }
                }
            }
            console.log(data)

            setTable(<>
                <section className={styles["selected-book-metadata"]}>
                    <p><b>Export SPARQL Result</b></p>
                    <ExportMenu options={[
                        { label: "JSON", href: `${process.env.REACT_APP_BACKEND_URL}download-qc-json?id=${file}` },
                        { label: "CSV", href: `${process.env.REACT_APP_BACKEND_URL}download-qc-csv?id=${file}` }
                    ]} />
                </section>
                <Grid data={data.table.data}
                columns={generatedCol}
                pagination={{ limit: 10 }}
                resizable={true}
                search={true} style={styleGrid} sort={true}
                language={ { search:{placeholder: "enter a keyword..."} }} />
                </>)

            const venusGraph = document.querySelector("#venus-graph")
            if (!venusGraph) { return }

            // Les requetes *_spo.rq n'utilisent pas toutes les memes noms de
            // variable (la plupart ont ?s/?o, mais qc1 par ex. utilise
            // ?author/?date a la place) : on choisit les champs source/cible
            // en fonction de ce qui existe reellement dans le resultat.
            const vars = spo_data?.head?.vars || []
            const pick = (candidates) => candidates.find((v) => vars.includes(v))
            const sourceField = pick(["s"]) || vars[0]
            const targetField = pick(["o", "date", "type"]) || vars[1]

            // Le champ animal (sourceField) a souvent des centaines de
            // valeurs distinctes (illisible d'un coup dans un graphe) : on
            // ne garde que les MAX_SOURCE_NODES animaux les plus frequents
            // avant de transmettre le resultat a VENUS, qui n'a pas de
            // notion de "top N" integree.
            const MAX_SOURCE_NODES = 20
            const sourceCounts = {}
            for (const b of spo_data?.results?.bindings || []) {
                const s = b[sourceField]?.value
                if (!s) continue
                sourceCounts[s] = (sourceCounts[s] || 0) + 1
            }
            const topSources = new Set(
                Object.entries(sourceCounts)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, MAX_SOURCE_NODES)
                    .map(([name]) => name)
            )
            const filteredResult = {
                head: spo_data.head,
                results: {
                    bindings: (spo_data?.results?.bindings || [])
                        .filter((b) => topSources.has(b[sourceField]?.value))
                }
            }

            venusGraph.sparqlResult = filteredResult
            venusGraph.encoding = {
                nodes: {
                    source: { field: sourceField, color: { value: '#4a6fa5' } },
                    target: { field: targetField, color: { value: '#9A6530' } }
                },
                links: { color: { value: '#ddccae' } },
                interactions: { drag: true, zoom: true, tooltip: true }
            }
            try {
                await venusGraph.launch()
            } catch (e) {
                console.error("VENUS: failed to render graph for this question", e)
            }

            /*setIframe(<iframe className={styles["iframe-box"]}
                title="Query visualisation"
                src={`${process.env.REACT_APP_LDVIZ_URL}ldviz?url=${process.env.REACT_APP_CORESE_URL}&query=${encodeURIComponent(data.spo)}&stylesheet=${encodeURIComponent(styleSheet)}`}
            >
            </iframe>)*/
            setTitleVizu(data.titleVizu)
        }
        callForData()
    }, [setTable, setIframe, styleGrid])

    useEffect(() => {
        const callForData = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}qcList`).then(response => response.json())
            const optionsList = []
            for (const row of data) {
                optionsList.push({ value: row.id, label: row.title })
            }
            setOptions(optionsList)
            if (optionsList.length > 0) {
                updateTable(optionsList[0])
            }
        }
        callForData()

    }, [setOptions, updateTable])

    return <div className={styles["box-content"]}>
        <header className={styles["box-header"]}>
            <span className={styles["field-label"]}>Competency question</span>
            <Select className={styles["input-select"]} placeholder={"select a competency question"} onChange={updateTable} options={options} value={selectedQuestion} />
        </header>
        <section className={styles["box-question"]}>
    {table}
    {titleVizu && <h3>{titleVizu}</h3>}
    <div style={{display: table ? 'block' : 'none'}}>
        <venus-graph id="venus-graph" className={styles["mge-dashboard"]} width="100%" height="600"></venus-graph>
    </div>
</section>

    </div>
}

export default CompetencyQuestionComponent;
