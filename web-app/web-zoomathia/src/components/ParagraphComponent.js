import { useState, useEffect, useCallback } from "react"
import styles from "./css_modules/ParagraphComponent.module.css"

const ParagraphDisplay = ({ id, text, uri, lang, concepts, controller }) => {
    const [text_content, setTextContent] = useState(<p key={`content-${id}`}>{text}</p>)
    const [nbConcept, setNbConcept] = useState(0)

    const redirectToOpenTheso = (e) => {
        window.open(e.target.getAttribute("uri"), "_blank")
    }

    const highlight = useCallback((e) => {
        const start = e.target.getAttribute('start')
        const end = e.target.getAttribute('end')
        const prefix = text.slice(0, start)
        const change = text.slice(start, end)
        const suffix = text.slice(end)
        setTextContent(<p key={`content-${id}`}>{prefix}<span className={styles["highlight"]}>{change}</span>{suffix}</p>)
    }, [text, id])

    const removeHighlight = useCallback((e) => {
        setTextContent(<p key={`content-${id}`}>{text}</p>)
    }, [id, text])

    return <section key={`paragraph-section-${id}`} className={styles["paragraph-section"]}>
        <div key={`paragraph-${id}`} id={uri} className={styles["id-paragraph"]}>
            <p key={`number-${id}`}>[{id}]</p>
        </div>
        <div key={`text-${id}`} className={styles["text-paragraph"]}>
            {text_content}
        </div>
        <div key={`concept-${id}`} className={styles['concept-list']}>
            <p>{concepts.length} concept{concepts.length > 1 ? 's' : ''}</p>
            <ul key={`concept-list-${id}`}>
                {concepts.map(annotation => {
                    return <li key={`concept_element_${annotation.annotation}${annotation.label}${lang}`}
                        uri={annotation.concept}
                        start={annotation.start} end={annotation.end}
                        onMouseEnter={highlight}
                        onMouseLeave={removeHighlight}
                        onClick={redirectToOpenTheso}>
                        {annotation.label}
                    </li>
                })}
            </ul>
        </div>
    </section>
}

export default ParagraphDisplay;