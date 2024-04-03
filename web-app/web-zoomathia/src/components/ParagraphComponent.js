import { useState, useEffect, useCallback } from "react"
import styles from "./css_modules/ParagraphComponent.module.css"

const ParagraphDisplay = (props) => {
    const [concepts, setConcepts] = useState([])
    const [text_content, setTextContent] = useState(<p key={`content-${props.id}`}>{props.text}</p>)
    const [nbConcept, setNbConcept] = useState(0)

    const redirectToOpenTheso = (e) => {
        window.open(e.target.getAttribute("uri"), "_blank")
    }

    const highlight = useCallback((e) => {
        const start = e.target.getAttribute('start')
        const end = e.target.getAttribute('end')
        const prefix = props.text.slice(0, start)
        const change = props.text.slice(start, end)
        const suffix = props.text.slice(end)
        setTextContent(<p key={`content-${props.id}`}>{prefix}<span className={styles["highlight"]}>{change}</span>{suffix}</p>)
    }, [props.text, props.id])

    const removeHighlight = useCallback((e) => {
        setTextContent(<p key={`content-${props.id}`}>{props.text}</p>)
    }, [props.id, props.text])

    useEffect(() => {
        const callForData = async () => {
            const conceptsList = []
            const data = await fetch(`http://localhost:3001/getConcepts?uri=${props.uri}&lang=${props.lang}`).then(response => response.json())
            for (const annotation of data) {
                conceptsList.push(
                    <li
                        key={`concept_element_${annotation.annotation}${annotation.label}${props.lang}`}
                        uri={annotation.concept}
                        start={annotation.start} end={annotation.end}
                        onMouseEnter={highlight}
                        onMouseLeave={removeHighlight}
                        onClick={redirectToOpenTheso}>
                        {annotation.label}
                    </li>
                )
            }
            setConcepts(conceptsList)
            setNbConcept(data.length)
        }
        callForData()
    }, [props.text, props.id, props.uri, props.lang, highlight, removeHighlight])

    return <section key={`paragraph-section-${props.id}`} className={styles["paragraph-section"]}>
        <div key={`paragraph-${props.id}`} className={styles["id-paragraph"]}>
            <p key={`number-${props.id}`}>[{props.id}]</p>
        </div>
        <div key={`text-${props.id}`} className={styles["text-paragraph"]}>
            {text_content}
        </div>
        <div key={`concept-${props.id}`} className={styles['concept-list']}>
            <p>{nbConcept} concept{nbConcept > 1 ? 's' : ''}</p>
            <ul key={`concept-list-${props.id}`}>
                {concepts}
            </ul>
        </div>
    </section>
}

export default ParagraphDisplay;