import { useState, useEffect, useCallback, useMemo } from "react"
import "gridjs/dist/theme/mermaid.min.css";
import styles from "./css_modules/CompetencyQuestionComponent.module.css"

import { Grid, _ } from "gridjs-react"
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

    const updateTable = useCallback((e) => {
        const file = e.value

        setTable(LOADING_STATE)
        setIframe(LOADING_STATE)

        const callForData = async () => {
            const generatedCol = []
            if (file === null) { return }
            const styleSheet = `{
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
                },
                "services": [
                    {
                        "label": "ACTA",
                        "url": "http://134.59.134.234:8081/analyseddocs?id="
                    },
                    {
                        "label": "Browser Corese",
                        "url": "http://corese.inria.fr/srv/service/covid?uri="
                    }
                ]
            }`
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getQC?id=${file}`).then(response => response.json())
            for (const elt of data.table.columns) {
                switch(elt){
                    case "paragraph":
                        generatedCol.push({
                            name: elt,
                            formatter: (cell) => { 
                                return html(`<a href='${process.env.REACT_APP_FRONTEND_URL}Work?uri=${cell}' target='_blank'>${cell.replace("http://www.zoomathia.com/", '')}</a>`) }
                        })
                        break;
                    case "name_anthroponym":
                        generatedCol.push({
                            name: elt,
                            formatter: (cell) => html(`<span class="${styles["anthroponym-variable"]}">${cell}</span>`)
                        })
                        break;
                    case "name_animal":
                        generatedCol.push({
                            name: elt,
                            formatter: (cell) => html(`<span class="${styles["animal-variable"]}">${cell}</span>`)
                        })
                        break;
                    default:
                        if(elt.includes("mention")){
                            generatedCol.push(elt)
                        }else{
                            generatedCol.push({
                                name: elt,
                                formatter: (cell) => html(`<span class="${styles["other-variable"]}">${cell}</span>`),
                            })
                        }
                }
            }
            console.log(html)

            setTable(<Grid data={data.table.data}
                columns={generatedCol}
                pagination={{ limit: 10 }}
                resizable={true}
                search={true} style={styleGrid} sort={true} 
                language={ { search:{placeholder: "filter row by keyword..."} }} />)

            setIframe(<iframe className={styles["iframe-box"]}
                title="Query visualisation"
                src={`${process.env.REACT_APP_LDVIZ_URL}ldviz?url=${process.env.REACT_APP_CORESE_URL}&query=${encodeURIComponent(data.spo)}&stylesheet=${encodeURIComponent(styleSheet)}`}
            >
            </iframe>)
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
            <Select className={styles["input-select"]} onChange={updateTable} options={options} />
        </header>
        <section className={styles["box-question"]}>
            {table}
            <h3>Visualisation</h3>
            {iframe}
        </section>

    </div>
}

export default CompetencyQuestionComponent;