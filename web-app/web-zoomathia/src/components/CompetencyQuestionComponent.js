import { useState, useEffect, useCallback } from "react"
import styles from "./css_modules/CompetencyQuestionComponent.module.css"
import "gridjs/dist/theme/mermaid.min.css";
import { Grid } from "gridjs-react"

const CompetencyQuestionComponent = () => {
    const [options, setOptions] = useState([])
    const [data, setData] = useState([])
    const [columns, setColumns] = useState([])
    const [title, setTitle] = useState("")
    const [goal, setGoal] = useState("")
    const [iframe, setIframe] = useState(<></>)

    const toSPOQuery = (query, s, p, o) => {
        return query.replace(s, "?s").replace(p, "?p").replace(o, "?o")
    }

    const updateTable = useCallback((e) => {
        const file = e.target.selectedOptions[0].getAttribute("id")
        const title = e.target.selectedOptions[0].label
        const callForData = async () => {
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
            setColumns(data.table.columns)
            setData(data.table.data)
            setGoal("My goal")
            setIframe(<iframe className={styles["iframe-box"]}
                title="Query visualisation"
                src={`${process.env.REACT_APP_LDVIZ_URL}ldviz?url=http://localhost:8080/sparql&query=${encodeURIComponent(data.spo)}&stylesheet=${encodeURIComponent(styleSheet)}`}
            //src={`http://dataviz.i3s.unice.fr/ldviz?url=http://54.36.123.165:8890/sparql&query=${encodeURIComponent(data.spo)}`}
            >
            </iframe>)
        }
        callForData()
    }, [setData, setColumns, setGoal, setIframe])

    useEffect(() => {
        const callForData = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}qcList`).then(response => response.json())
            const optionsList = [<option></option>]
            for (const row of data) {
                optionsList.push(<option key={row.id} id={row.id} data={row.file}>QC{row.id} - {row.title}</option>)
            }
            setOptions(optionsList)

        }
        callForData()

    }, [setOptions])

    return <div className={styles["box-content"]}>
        <h2>Select a competency question</h2>
        <select onChange={updateTable}>
            {options}
        </select>
        <h3>{title}</h3>
        <div>
            <p><u>Goal:</u> {goal}</p>
        </div>
        <Grid data={data} columns={columns} pagination={{ limit: 20 }} search={true} />
        <h3>Visualisation</h3>
        {iframe}
    </div>
}

export default CompetencyQuestionComponent;