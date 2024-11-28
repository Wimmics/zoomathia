import { useState, useEffect, useCallback, useMemo } from "react"
import "gridjs/dist/theme/mermaid.min.css";
import styles from "./css_modules/CompetencyQuestionComponent.module.css"

import { Grid } from "gridjs-react"
import { html } from 'gridjs'
import Select from 'react-select'

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
    const [iframe, setIframe] = useState(<></>)
    const [table, setTable] = useState(null)
    const [titleVizu, setTitleVizu] = useState('')

    const updateTable = useCallback((e) => {
        const file = e.value
        setTable(LOADING_STATE)
        setIframe(LOADING_STATE)

        const callForData = async () => {
            const generatedCol = []
            if (file === null) { return }
            const styleSheet = {
                "appli": {
                    "name": "ldviz",
                    "debug": true
                },
                "node": {
                    "default": {
                        "color": "steelblue"
                    },
                    "mix": {
                        "color": "yellow"
                    },
                    "member": {
                        "color": "purple"
                    },
                    "other": {
                        "color": "green"
                    },
                    "fst": {
                        "color": "red",
                        "priority": 1
                    },
                    "snd": {
                        "color": "orange",
                        "priority": 2
                    },
                    "rst": {
                        "color": "green",
                        "priority": 3
                    }
                },
                "edge": {
                    "color": "green"
                }
            }
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
                <p><b>Export SPARQL Result</b>: 
                        <a className={styles["button-export"]} 
                        href={`${process.env.REACT_APP_BACKEND_URL}download-qc-json?id=${file}`}  
                        download target="_blank" rel="noreferrer">JSON</a>

                        <a className={styles["button-export"]} 
                        href={`${process.env.REACT_APP_BACKEND_URL}download-qc-csv?id=${file}`}  
                        download target="_blank" rel="noreferrer">CSV</a>
                    </p>
                </section>
                <Grid data={data.table.data}
                columns={generatedCol}
                pagination={{ limit: 10 }}
                resizable={true}
                search={true} style={styleGrid} sort={true} 
                language={ { search:{placeholder: "filter row by keyword..."} }} />
                </>)

            const mgeDashboard = document.querySelector("#mge-dashboard")
            mgeDashboard.resetDashboard()
            mgeDashboard.disableInitialQueryPanel()
            mgeDashboard.disableView("mge-glyph-matrix")
            mgeDashboard.disableView("mge-clustervis")
            mgeDashboard.disableView("mge-annotation")
            mgeDashboard.disableView("mge-query")
            

            mgeDashboard.setData(spo_data, styleSheet)
            mgeDashboard.setDashboard()


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
        }
        callForData()

    }, [setOptions])

    return <div className={styles["box-content"]}>
        <header className={styles["box-header"]}>
            <h2 key="titre_competence">Select a competency question</h2>
            <Select className={styles["input-select"]} placeholder={"Select a competency question"} onChange={updateTable} options={options} />
        </header>
        <section className={styles["box-question"]}>
            {table}
            <h3>{titleVizu}</h3>
            <div>
                <mge-dashboard id="mge-dashboard" className={styles["mge-dashboard"]}></mge-dashboard>
            </div>
            
        </section>

    </div>
}

export default CompetencyQuestionComponent;