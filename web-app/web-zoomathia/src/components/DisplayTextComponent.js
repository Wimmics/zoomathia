import { useState, useRef, useEffect } from "react";
import SectionComponent from './SectionComponent'
import styles from "./css_modules/BookComponents.module.css"
import Summary from "./Summary.js"
import { SimpleTreeView } from "@mui/x-tree-view";
import Grid from '@mui/material/Grid2';

const DisplayTextComponent = ({ controller, uri, options, type }) => {
    const [sections, setSections] = useState([])
    const [metadata, setMetadata] = useState({})
    const [summary, setSummary] = useState(null)
    const [currentBook, setCurrentBook] = useState(null)
    const controllerRef = useRef(controller.current)

    const handleToc = async (uri, nodeTitle) => {
        if (controllerRef.current) {
            controllerRef.current.abort()
        }
        controllerRef.current = new AbortController()

        setSections(<SectionComponent sectionTitle={nodeTitle} uri={uri} controller={controllerRef} />)

    }

    const setChange = (e, title) => {
        handleToc(e, title)
    }
    
    useEffect(() => {
        const getMetadata = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getMetadata?uri=${uri}`)
                .then(response => response.json())
            setMetadata(data)
        }

        const getSummary = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getSummary?uri=${uri}`)
                .then(response => response.json())
            setSummary(data)
            setSections(<SectionComponent sectionTitle={data[0].title} uri={data[0].uri} controller={controllerRef} />)
            setCurrentBook(data[0].uri)
        }

        getMetadata()
        getSummary()
        return () => {
            setSummary(null)
            setMetadata({})
        }
    }, [options, type, uri])

    return <section>
        <section className={styles["selected-book-metadata"]}>
            <div className={styles["metadata-div"]}>
                <p><b>Editor</b>: {metadata.editor}</p>
            </div>
            <div className={styles["metadata-div"]}>
                <p><b>Year</b>: {metadata.date}</p>
            </div>
            <div className={styles["metadata-div"]}>
                <p><b>Export</b>: 
                    <a className={styles["button-export"]} 
                        href={`${process.env.REACT_APP_BACKEND_URL}download-xml?file=${metadata.file}`} 
                        download={metadata.file} target="_blank" rel="noreferrer">XML-TEI</a>
                    <a className={styles["button-export"]} 
                        href={`${process.env.REACT_APP_BACKEND_URL}download-turtle?uri=${uri}`}  
                        download target="_blank" rel="noreferrer">Turtle</a>
                </p>
            </div>
        </section>
        <Grid container spacing={2}>
            <Grid size={2}>
                <section className={styles["section-toc"]}>
                    <h2>Table of contents</h2>
                    <div className={styles["ul-toc"]}>
                        <ul>
                            {summary !== null ? summary.map(node => <SimpleTreeView key={node.uri}>
                                <Summary key={node.uri} node={node} currentBook={currentBook} setChange={setChange} setCurrentBook={setCurrentBook} />
                                </SimpleTreeView>
                            ) : ''}
                        </ul>
                    </div>
                </section>
            </Grid>
            <Grid size={10}>
                {sections}
            </Grid>
        </Grid>
    </section>
}

export default DisplayTextComponent;

/*<button className={styles["button-export"]} onClick={downloadRDF}>Turtle</button>*/