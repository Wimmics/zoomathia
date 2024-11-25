import { useState, useCallback, useEffect, useRef } from "react"
import styles from "./css_modules/ParagraphComponent.module.css"
import redirection from "./css_modules/logo/redirect-svgrepo-com.svg"

const ListElement = ({uri, label, type, offsets, onMouseEnter, onMouseLeave, onClick}) => {
    return <li className={
        uri.includes("wikidata") ? styles["wikidata-annotation"] :
        uri.includes("dbpedia") ? styles["dbpedia-annotation"] : styles["manual-annotation"]}  onMouseEnter={() => onMouseEnter(offsets)} onMouseLeave={onMouseLeave} onClick={() => {onClick(uri)}}>
        {label}
    </li>

}

const ParagraphDisplay = ({ id, text, uri, lang, concepts, controller, displayId, redirect }) => {
    const [text_content, setTextContent] = useState(<p key={`content-${id}`}>{text}</p>)
    const [conceptsDiv, setConceptsDiv] = useState([])
    const controllerRef = useRef(controller)

    const redirectToOpenTheso = (e) => {
        window.open(e, "_blank")
    }

    const highlight = useCallback((offsets) => {
        setTextContent(<p key={`content-${id}`}>
            {text.slice(0, offsets[0].start)}<span className={styles["highlight"]}>{text.slice(offsets[0].start, offsets[0].end)}</span>{text.slice(offsets[0].end, text.length)}
            </p>)
    }, [text, id])

    const removeHighlight = useCallback((e) => {
        setTextContent(<p key={`content-${id}`}>{text}</p>)
    }, [id, text])

    useEffect(() => {
        const getConcepts = async () => {
            try {
                let concepts_data
                if(concepts.length <= 0){
                    const signal = controllerRef.current.signal
                    concepts_data = await fetch( 
                        `${process.env.REACT_APP_BACKEND_URL}getConcepts?uri=${uri}&lang=${"en"}`, 
                        {signal}
                    ).then(response => response.json())
                } else {
                    concepts_data = concepts
                }

                const concepts_list = []
                for(const annotation of Object.keys(concepts_data)){
                    const offsets = concepts_data[annotation].offset
                    concepts_list.push(
                    <ListElement key={`concept_element_${concepts_data[annotation].label}${lang}`}
                        uri={concepts_data[annotation].concept}
                        label={concepts_data[annotation].label}
                        type={concepts_data[annotation].type}
                        offsets={offsets}
                        onMouseEnter={highlight}
                        onMouseLeave={removeHighlight}
                        onClick={redirectToOpenTheso} />
                    )
                }

                setConceptsDiv(<div key={`concept-${id}`} className={styles['concept-list']}>
                    <p><b>{Object.keys(concepts_list).length} concept{Object.keys(concepts_list).length > 1 ? 's' : ''}</b></p>
                    <ul key={`concept-list-${id}`}>
                        {concepts_list}  
                    </ul>
                </div>)
            }catch(err){
                console.log(err)
            }
    }

        getConcepts()
    }, [highlight, id, lang, removeHighlight, uri, concepts])

    return <section key={`paragraph-section-${id}`} className={styles["paragraph-section"]}>
        <div key={`paragraph-${id}`} id={uri} className={styles["id-paragraph"]}>
            {displayId ? <p key={`number-${id}`}>{`[${parseInt(id)}]`}</p> : <p key={`number-${id}`}></p>}
            {true ? <a href={`${process.env.REACT_APP_FRONTEND_URL}ExploreAWork?uri=${uri}`} rel="noreferrer" target="_blank">
                <img className={styles["logo-redirect"]} src={redirection} alt=""/>
                </a> : ""}
        </div>
        <div key={`text-${id}`} className={styles["text-paragraph"]}>
            {text_content}
        </div>
        {conceptsDiv}
    </section>
}

export default ParagraphDisplay;