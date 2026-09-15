import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import ParagraphDisplay from "./ParagraphComponent"
import styles from "./css_modules/BookComponents.module.css"

const LOADING_STATE = <>
    <div className={styles["loader"]}></div>
    <p>Loading work...</p>
</>

const Work = () => {
    const [searchParams] = useSearchParams();
    const [paragraph, setParagraph] = useState(LOADING_STATE)
    //const [title, setTitle] = useState(null)
    const [focus, setFocus] = useState(false)
    const controllerRef = useRef(null)

    const uri = searchParams.get('uri');

    useEffect(() => {
        if (focus) {
            const elementToFocus = document.getElementById(uri)
            elementToFocus.scrollIntoView({ behaviour: 'smooth', block: 'center' })
        }
    })

    useEffect(() => {
        if (controllerRef.current) {
            controllerRef.current.abort()
        }
        controllerRef.current = new AbortController()
        const signal = controllerRef.current.signal

        const callForData = async () => {
            const paragraphs = []
            const data = await fetch(
                `${process.env.REACT_APP_BACKEND_URL}getParagraphAlone?uri=${uri}`,
                { signal }
            ).then(response => response.json())
            // Le texte est deja disponible ici (getParagraphAlone, independant des
            // annotations) : on l'affiche tout de suite, ParagraphDisplay se
            // chargeant lui-meme de recuperer ses concepts en arriere-plan (voir
            // SectionComponent pour le meme correctif et son explication).
            for (const elt of data) {
                paragraphs.push(<ParagraphDisplay
                    key={elt.uri}
                    id={elt.id}
                    text={elt.text}
                    uri={elt.uri}
                    lang={"en"}
                    concepts={[]}
                    controller={controllerRef} />)
            }
            setParagraph(paragraphs)
            setFocus(true)
        }
        callForData()
    }, [uri])

    return <div className={styles["box-content"]}>
        <header className={styles["selected-book-title"]}>
            <h2>{uri}</h2>
        </header>

        {paragraph}
    </div >
}

export default Work;