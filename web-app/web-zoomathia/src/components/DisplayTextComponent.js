import { useState, useEffect } from "react";
import { useSearchParams } from 'react-router-dom';
import SectionComponent from './SectionComponent'
import styles from "./css_modules/BookComponents.module.css"
import Summary from "./Summary.js"
import ExportMenu from "./ExportMenu"
import { SimpleTreeView } from "@mui/x-tree-view";
import Grid from '@mui/material/Grid2';

const DisplayTextComponent = ({ controller, uri, options, type }) => {
    const [currentSection, setCurrentSection] = useState(null)
    const [metadata, setMetadata] = useState({})
    const [summary, setSummary] = useState(null)
    const [currentBook, setCurrentBook] = useState(null)
    const [translation, setTranslation] = useState(null)
    const [showTranslation, setShowTranslation] = useState(false)

    const [searchParams, setSearchParams] = useSearchParams();
    const paramsUri = searchParams.get('uri');

    const handleToc = async (sectionUri, nodeTitle) => {
        setCurrentSection(null)
        setSearchParams("")
        /*if (controllerRef.current) {
            controllerRef.current.abort("Changing work from table of content")
        }
        controllerRef.current = new AbortController()*/

        setCurrentSection({ uri: sectionUri, title: nodeTitle })

    }

    const setChange = (e, title) => {
        if(e !== currentBook){
            setCurrentBook(e)
            handleToc(e, title)
        }

    }

    useEffect(() => {

        const getMetadata = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getMetadata?uri=${uri}`)
                .then(response => response.json())
            setMetadata(data)
        }

        const getTranslation = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getTranslation?uri=${uri}`)
                .then(response => response.json())
                .catch(() => null)
            setTranslation(data)
            if (data) { setShowTranslation(true) }
        }

        const getSummary = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getSummary?uri=${uri}`)
                .then(response => response.json())
            console.log(data)
            setSummary(data)

            /* This part is called only if searchParams is given
             * Get the book that include the given URI, if the URI is a Work, set to the first child
             */
            if(searchParams && (data[0].uri.length <= paramsUri?.length)){
                for(const book of data){
                    if( paramsUri.includes(book.uri)){
                        setCurrentSection({ uri: book.uri, title: book.title })
                        setCurrentBook(book.uri)
                    }
                }
            }else{
                setCurrentSection({ uri: data[0].uri, title: data[0].title })
                setCurrentBook(data[0].uri)
            }

        }

        setShowTranslation(false)
        getMetadata()
        getTranslation()
        getSummary()
    }, [options, type, uri, controller, paramsUri, searchParams, setSearchParams])

    return <section>
        <section className={styles["selected-book-metadata"]}>
            <div className={styles["work-info"]}>
                <div className={styles["metadata-div"]}>
                    <p><b>Editor</b>: {metadata.editor}</p>
                </div>
                <div className={styles["metadata-div"]}>
                    <p><b>Year</b>: {metadata.date}</p>
                </div>
            </div>
            <div className={styles["interface-actions"]}>
                {translation && <label className={styles["translation-toggle"]}>
                    <input type="checkbox" checked={showTranslation} onChange={(e) => setShowTranslation(e.target.checked)} />
                    Show English translation ({translation.title})
                </label>}
                <ExportMenu options={[
                    { label: "XML-TEI", href: `${process.env.REACT_APP_BACKEND_URL}download-xml?file=${metadata.file}`, download: metadata.file },
                    { label: "Turtle", href: `${process.env.REACT_APP_BACKEND_URL}download-turtle?uri=${uri}` }
                ]} />
            </div>
        </section>
        <Grid container spacing={2}>
            <Grid size={2}>
                <section className={styles["section-toc"]}>
                    <h2>Table of contents</h2>
                    <div className={styles["ul-toc"]}>
                        <ul>
                            {summary !== null ? summary.map(node =>
                                <SimpleTreeView key={node.uri}>
                                    <Summary key={node.uri} node={node} currentBook={currentBook} setChange={setChange} setCurrentBook={setCurrentBook} />
                                </SimpleTreeView>
                            ) : ''}
                        </ul>
                    </div>
                </section>
            </Grid>
            <Grid size={10}>
                {currentSection && <SectionComponent
                    key={`${currentSection.uri}-${showTranslation}`}
                    sectionTitle={currentSection.title}
                    uri={currentSection.uri}
                    workUri={uri}
                    translationWorkUri={showTranslation ? translation?.uri : null}
                    controller={controller} />}
            </Grid>
        </Grid>
    </section>
}

export default DisplayTextComponent;

/*<button className={styles["button-export"]} onClick={downloadRDF}>Turtle</button>*/