import { useState, useEffect, useCallback } from "react"
import styles from "./css_modules/CompetencyQuestionComponent.module.css"
import "gridjs/dist/theme/mermaid.min.css";
import { Grid } from "gridjs-react"

const CompetencyQuestionComponent = () => {
    const [options, setOptions] = useState([])
    const [data, setData] = useState([])
    const [columns, setColumns] = useState([])
    const [title, setTitle] = useState("")

    const updateTable = useCallback((e) => {
        const file = e.target.selectedOptions[0].getAttribute("data")
        const title = e.target.selectedOptions[0].label
        const callForData = async () => {
            if (file === null) { return }
            const data = await fetch(`http://localhost:3001/getQC?id=${file}`).then(response => response.json())
            setTitle(title)
            setColumns(data.table.columns)
            setData(data.table.data)
        }
        callForData()
    }, [setData, setColumns])

    useEffect(() => {
        const callForData = async () => {
            const data = await fetch(`http://localhost:3001/qcList`).then(response => response.json())
            const optionsList = [<option></option>]
            for (const row of data) {
                optionsList.push(<option key={row.id} id={row.id} data={row.file}>QC{row.id} - {row.title}</option>)
            }
            setOptions(optionsList)

        }
        callForData()

    }, [setOptions])

    return <div className={styles["box-content"]}>
        <select onChange={updateTable}>
            {options}
        </select>
        <h2>{title}</h2>
        <Grid data={data} columns={columns} pagination={{ limit: 5 }} search={true} />
    </div>
}

export default CompetencyQuestionComponent;