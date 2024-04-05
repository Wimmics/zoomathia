import { useState, useEffect } from "react"
import styles from "./css_modules/CompetencyQuestionComponent.module.css"
import "gridjs/dist/theme/mermaid.min.css";
import { Grid } from "gridjs-react"

const CompetencyQuestionComponent = () => {
    const [data, setData] = useState([])
    const [columns, setColumns] = useState([])

    useEffect(() => {
        console.log("Called useEffect")
        const callForData = async () => {
            console.log("Called callForData")
            const data = await fetch(`http://localhost:3001/getQC?id=1`).then(response => response.json())
            console.log(data)
            setColumns(data.table.columns)
            setData(data.table.data)
        }
        callForData()

    }, [setData, setColumns])

    return <div className={styles["box-content"]}>
        <select>
            <option></option>
            <option>Question 1</option>
            <option>Question 2</option>
        </select>
        <Grid data={data} columns={columns} pagination={{ limit: 5 }} search={true} />
    </div>
}

export default CompetencyQuestionComponent;