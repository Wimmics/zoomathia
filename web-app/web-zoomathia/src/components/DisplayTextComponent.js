import { useState, useEffect } from "react";
import { useSearchParams } from 'react-router-dom';
import SectionComponent from './SectionComponent'
import styles from "./css_modules/BookComponents.module.css"
import Summary from "./Summary.js"
import ExportMenu from "./ExportMenu"
import { SimpleTreeView } from "@mui/x-tree-view";
import Grid from '@mui/material/Grid2';

// Reduit un sommaire imbrique (livres/chapitres/sections) a la liste, dans
// l'ordre du texte, de ses feuilles (les noeuds sans enfants - les
// paragraphes en sont deja exclus par /getSummary). C'est a ce niveau que
// vivent les paragraphes.
const flattenLeaves = (nodes) => {
    const leaves = []
    for (const node of nodes || []) {
        if (!node.children || node.children.length === 0) {
            leaves.push(node.uri)
        } else {
            leaves.push(...flattenLeaves(node.children))
        }
    }
    return leaves
}

const DisplayTextComponent = ({ controller, uri, options, type }) => {
    const [currentSection, setCurrentSection] = useState(null)
    const [metadata, setMetadata] = useState({})
    const [summary, setSummary] = useState(null)
    const [currentBook, setCurrentBook] = useState(null)
    const [translationSummary, setTranslationSummary] = useState(null)
    const [translationMap, setTranslationMap] = useState(null)

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
            if (data) {
                // Lance tout de suite le sommaire de la traduction, en
                // parallele de celui de l'oeuvre originale (pas apres),
                // pour ne pas doubler le temps d'attente deja eleve de
                // /getSummary.
                fetch(`${process.env.REACT_APP_BACKEND_URL}getSummary?uri=${data.uri}`)
                    .then(response => response.json())
                    .then(setTranslationSummary)
                    .catch(() => null)
            }
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

        setTranslationSummary(null)
        setTranslationMap(null)
        getMetadata()
        getTranslation()
        getSummary()
    }, [options, type, uri, controller, paramsUri, searchParams, setSearchParams])

    useEffect(() => {
        // Les editions dans differentes langues d'une meme oeuvre n'ont pas
        // toujours exactement la meme profondeur de structure (ex. un niveau
        // de regroupement en plus cote grec) : on apparie donc les chapitres
        // par leur position dans l'ordre du texte plutot que par leur URI,
        // ce qui reste correct meme si l'imbrication differe.
        if (!summary || !translationSummary) { return }

        const originalLeaves = flattenLeaves(summary)
        const translationLeaves = flattenLeaves(translationSummary)

        // Sur environ deux tiers des oeuvres du corpus, l'original et sa
        // traduction ne se decoupent pas dans le meme nombre de sections
        // (edition differente, granularite d'annotation differente...).
        // Un appariement par position deviendrait alors faux au-dela du
        // point de divergence : preferable de ne pas afficher de
        // traduction du tout plutot qu'une traduction qui ne correspond
        // plus au bon passage.
        if (originalLeaves.length !== translationLeaves.length) { return }

        const map = {}
        for (let i = 0; i < originalLeaves.length; i++) {
            map[originalLeaves[i]] = translationLeaves[i]
        }
        setTranslationMap(map)
    }, [summary, translationSummary])

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
                    key={currentSection.uri}
                    sectionTitle={currentSection.title}
                    uri={currentSection.uri}
                    translationMap={translationMap}
                    controller={controller} />}
            </Grid>
        </Grid>
    </section>
}

export default DisplayTextComponent;

/*<button className={styles["button-export"]} onClick={downloadRDF}>Turtle</button>*/