import { useState, useEffect } from "react";
import { useSearchParams } from 'react-router-dom';
import SectionComponent from './SectionComponent'
import styles from "./css_modules/BookComponents.module.css"
import Summary from "./Summary.js"
import ExportMenu from "./ExportMenu"
import { SimpleTreeView } from "@mui/x-tree-view";
import Grid from '@mui/material/Grid2';

// Certains temoins ajoutent un niveau d'enveloppe qui n'est pas une vraie
// reference (juste un artefact d'encodage, ex. le div racine d'un fichier
// sans structure propre) : on l'ignore pour ne comparer que les vrais
// niveaux de citation.
const MEANINGLESS_TYPES = new Set(["UnidentifiedPart"])

// Reduit un sommaire imbrique (livres/chapitres/sections) a la liste de ses
// feuilles (les noeuds sans enfants - les paragraphes en sont deja exclus
// par /getSummary), chacune associee a son chemin de reference reel (type
// + numero a chaque niveau, ex. Chapter 3 > Section 9). Ce chemin sert a
// apparier deux temoins par ce qu'ils designent reellement, plutot que par
// leur position ou leur profondeur d'imbrication qui peuvent differer d'une
// edition a l'autre.
const collectLeaves = (nodes, path = []) => {
    const leaves = []
    for (const node of nodes || []) {
        const nodeType = node.type?.split('#').pop()
        const nextPath = MEANINGLESS_TYPES.has(nodeType) ? path : [...path, `${nodeType}:${node.id}`]
        if (!node.children || node.children.length === 0) {
            leaves.push({ uri: node.uri, key: nextPath.join('/') })
        } else {
            leaves.push(...collectLeaves(node.children, nextPath))
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
        // Les editions dans differentes langues d'une meme oeuvre ne se
        // decoupent pas toujours en autant de sections, ni au meme niveau
        // d'imbrication (edition differente, granularite differente...).
        // On apparie donc chaque section par ce qu'elle designe vraiment
        // (son chemin de reference : Chapter 3 > Section 9, par exemple),
        // pas par sa position dans le texte. Une section sans equivalent
        // exact de l'autre cote n'affiche simplement pas de traduction,
        // plutot que d'en afficher une qui ne correspond pas au bon passage.
        if (!summary || !translationSummary) { return }

        const originalLeaves = collectLeaves(summary)
        const translationByKey = {}
        for (const leaf of collectLeaves(translationSummary)) {
            translationByKey[leaf.key] = leaf.uri
        }

        const map = {}
        for (const leaf of originalLeaves) {
            if (translationByKey[leaf.key]) {
                map[leaf.uri] = translationByKey[leaf.key]
            }
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