import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import ParagraphDisplay from "./ParagraphComponent"
import styles from "./css_modules/BookComponents.module.css"

const Work = () => {
    const [searchParams] = useSearchParams();
    const [paragraph, setParagraph] = useState(null)
    const [title, setTitle] = useState(null)
    const controllerRef = useRef(null)

    const uri = searchParams.get('uri');

    useEffect(() => {
        if(controllerRef.current){
            controllerRef.current.abort()
        }
        controllerRef.current = new AbortController()
        const signal = controllerRef.current.signal

        const callForData = async () => {
            const paragraphs = []
            console.log(process.env.REACT_APP_BACKEND_URL)
            console.log(uri)
            const data = await fetch(
                `${process.env.REACT_APP_BACKEND_URL}getParagraphAlone?uri=${uri}`,
                { signal }
            ).then(response => response.json())
            for (const elt of data) {
                paragraphs.push(<ParagraphDisplay
                    key={elt.id}
                    id={elt.id}
                    text={elt.text}
                    uri={elt.uri}
                    lang={"en"}
                    controller={controllerRef} />)
            }
            setParagraph(paragraphs)
        }
        callForData()
    },[])

    return <div className={styles["box-content"]}>
        <header className={styles["selected-book-title"]}>
        <h2>{uri}</h2>
        </header>
        
        {paragraph}
    </div >
}

export default Work;