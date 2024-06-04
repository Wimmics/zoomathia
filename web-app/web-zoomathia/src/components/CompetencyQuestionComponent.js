import { useState, useEffect, useCallback } from "react"
import styles from "./css_modules/CompetencyQuestionComponent.module.css"
import "gridjs/dist/theme/mermaid.min.css";
import { Grid } from "gridjs-react"
import { html } from 'gridjs'
import Select from 'react-select'

const CompetencyQuestionComponent = () => {
    const styleGrid = {
        td: {
            'text-overflow': 'ellipsis',
            'overflow': 'hidden',
            'white-space': 'normal'
        }
    }

    const [options, setOptions] = useState([])
    const [title, setTitle] = useState("")
    const [iframe, setIframe] = useState(<></>)
    const [table, setTable] = useState(<Grid data={[]} columns={[]} pagination={{ limit: 10 }} search={true} style={styleGrid} />)

    const updateTable = useCallback((e) => {
        const file = e.value
        const title = e.label
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
                        "color": "purple",
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
            setTitle(title)
            for (const elt of data.table.columns) {
                if (elt === "paragraph") {
                    generatedCol.push({
                        name: elt,
                        formatter: (cell) => { return html(`<a href='${process.env.REACT_APP_FRONTEND_URL}Work?uri=${cell}' target='_blank'>${cell.replace("http://www.zoomathia.com/", '')}</a>`) }
                    })
                } else {
                    generatedCol.push(elt)
                }
            }
            console.log(html)
            setTable(<Grid data={data.table.data} columns={generatedCol} pagination={{ limit: 10 }} search={true} style={styleGrid} sort={true} />)
            setIframe(<iframe className={styles["iframe-box"]}
                title="Query visualisation"
                src={`${process.env.REACT_APP_LDVIZ_URL}ldviz?url=${process.env.REACT_APP_CORESE_URL}&query=${encodeURIComponent(data.spo)}&stylesheet=${encodeURIComponent(styleSheet)}`}
            >
            </iframe>)
        }
        callForData()
    }, [setTable, setIframe])

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
        <header>
            <h2 key="titre_competence">Select a competency question</h2>
            <Select onChange={updateTable} options={options} />
        </header>
        <h3>{title}</h3>
        {table}
        <h3>Visualisation</h3>
        {iframe}
    </div>
}

export default CompetencyQuestionComponent;