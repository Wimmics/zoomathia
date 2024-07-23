import { useState, useRef, useEffect } from "react";
import SectionComponent from './SectionComponent'
import Select from 'react-select'
import styles from "./css_modules/BookComponents.module.css"
import ParagraphDisplay from "./ParagraphComponent";

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const Summary = ({ node, currentBook, setChange, setCurrentBook }) => {
    const handleDisplay = () => {
        console.log(node.title)
        /* Check if the current display should be regenerated */
        if (!node.uri.includes(currentBook)) {
            console.log(`not includes currentBook=${currentBook} and node.uri=${node.uri}`)
            if(getTypeFromURI(node.type) === "Book"){
                setCurrentBook(node.uri)
            }/*else{
                const highest_level = node.uri.split("/")
                setCurrentBook(highest_level[0]+'/'+highest_level[1])
            }*/
            setChange(node.uri, node.title)
        }
    }

    const handleClick = async () => {

        const element = document.getElementById(node.uri)
        handleDisplay()
        if (!element) {
            console.log(`Cannot select element on URI ${node.uri}`)
        } else if (element && node.type !== "http://www.zoomathia.com/2024/zoo#Paragraph") {
            element.scrollIntoView({ behaviour: 'smooth', block: 'start' })
        } else {
            element.scrollIntoView({ behaviour: 'smooth', block: 'center' })

        }
    }
    return <li id={node.type + "_" + node.id + "_summary"} key={node.uri + "_summary"}>
        <details>
            <summary>
                <button className={styles["button-toc"]} onClick={handleClick}>
                    {getTypeFromURI(node?.type)} - {node.title !== '' ? node.title : node.id}
                </button>
            </summary>
            {node.children && node.children.length > 1 && (<ul>
                {node.children.map(child => <Summary
                    key={`${child.uri}_${node.id}_summary`}
                    node={child}
                    currentBook={currentBook}
                    setChange={setChange} setCurrentBook={setCurrentBook}/>)}
                    
            </ul>)}
        </details>
    </li>
}

const DisplayTextComponent = ({ controller, uri, options, type }) => {
    const [sections, setSections] = useState([])
    const [selectInput, setSelectInput] = useState([])
    const [metadata, setMetadata] = useState({})
    const [summary, setSummary] = useState(null)
    const [currentBook, setCurrentBook] = useState(null)
    const controllerRef = useRef(controller.current)

    //const [currentLang, setCurrentLang] = useState('en')

    /*const searchConcepts = async (input) => {
        const retrieved_concept = []
        const callForData = async (input) => {
            if (input === '') {
                return []
            } else {
                const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}searchConcepts?input=${input}&lang=${currentLang}`)
                    .then(response => response.json())
                for (const concept of data) {
                    retrieved_concept.push({ value: concept.uri, label: `${concept.label}@${currentLang}` })
                }
                return retrieved_concept
            }
        }
        return await callForData(input)
    }*/

    const getParagraph = async (e, signal) => {

        const data = await fetch(
            `${process.env.REACT_APP_BACKEND_URL}getParagraphAlone?uri=${e.value}`,
            { signal }
        ).then(response => response.json())

        const para = []
        for (const elt of data) {

            const concepts_list = await fetch(
                `${process.env.REACT_APP_BACKEND_URL}getConcepts?uri=${elt.uri}&lang=${"en"}`,
                { signal }
            ).then(response => response.json())

            para.push(<ParagraphDisplay
                key={elt.id}
                id={elt.id}
                text={elt.text}
                uri={elt.uri}
                lang={"en"}
                concepts={concepts_list}
                controller={controllerRef} />)
        }
        return para
    }

    const getChildrenType = async (selectedOption, signal) => {
        let childType = ''
        const checkType = await fetch(
            `${process.env.REACT_APP_BACKEND_URL}getChildrenType?uri=${selectedOption.value}`,
            { signal }
        ).then(response => response.json())

        for (const elt of checkType) {
            childType = getTypeFromURI(elt)
        }
        return childType
    }

    const getOptions = async (selectedOption, signal) => {
        const childOptions = []
        const data = await fetch(
            `${process.env.REACT_APP_BACKEND_URL}getChildren?uri=${selectedOption.value}`,
            { signal }
        ).then(response => response.json())

        for (const elt of data) {
            childOptions.push({
                label: elt.title,
                value: elt.uri,
                type: elt.type
            })
        }
        return childOptions
    }

    const handleToc = async (uri, nodeTitle) => {
        if (controllerRef.current) {
            controllerRef.current.abort()
        }
        controllerRef.current = new AbortController()

        setSections(<SectionComponent sectionTitle={nodeTitle} uri={uri} controller={controllerRef} />)

    }

    const handleSelect = async (i, selectedOption) => {
        if (controllerRef.current) {
            controllerRef.current.abort()
        }
        controllerRef.current = new AbortController()
        const signal = controllerRef.current.signal



        if (getTypeFromURI(selectedOption.type) === "Paragraph") {
            const newSelects = selectInput.slice(0, i + 1).map((select, index) => {
                return select;
            })
            setSelectInput(newSelects)
            setSections([])
            const paragraph = await getParagraph(selectedOption)
            setSections(paragraph)
            return
        }

        const newSelects = selectInput.slice(0, i + 1).map((select, index) => {
            if (i === index) {
                return { ...select, value: selectedOption }
            }
            return select;
        })
        setCurrentBook(selectedOption.value)
        if (i === selectInput.length - 1) {
            const newId = selectInput.length + 1;
            const newType = await getChildrenType(selectedOption, signal);
            const newOptions = await getOptions(selectedOption, signal);
            setSelectInput([...newSelects, { id: newId, type: newType, options: newOptions }])
            setSections([])
            const uri = selectedOption.value
            const title = selectedOption.label
            setSections(<SectionComponent sectionTitle={title} uri={uri} controller={controllerRef} />)
        } else {
            setSections([])
            const uri = selectedOption.value
            const title = selectedOption.label
            setSections(<SectionComponent sectionTitle={title} uri={uri} controller={controllerRef} />)
        }

    }

    const downloadRDF = () => {
        console.log("subgraph download...")
    }

    const downloadTEI = () => {
        console.log("XML-TEI download...")
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
        }
        const update = async () => {
            setSelectInput([{ id: 0, type: type, options: options }])
        }

        update()
        getMetadata()
        getSummary()
        return () => {
            update()
            setSelectInput([])
            setSummary(null)
            setMetadata({})
        }
    }, [options, type, uri])

    return <section>
        <section className={styles["metadata-section"]}>
            <div className={styles["metadata-div"]}>
                <p><b>Editor</b>: {metadata.editor}</p>
            </div>
            <div className={styles["metadata-div"]}>
                <p><b>Date</b>: {metadata.date}</p>
            </div>
            <div className={styles["metadata-div"]}>
                <p><b>Export XML-TEI</b>: 
                    <button title={metadata.file} className={styles["button-export"]} onClick={downloadTEI} data={metadata.file}>XML-TEI
                    </button></p>
            </div>
            <div className={styles["metadata-div"]}>
                <p><b>Export RDF</b>: <button className={styles["button-export"]} onClick={downloadRDF}>Turtle</button></p>
            </div>
        </section>
        <section className={styles["selection-section"]}>
            {selectInput.map((select, index) => {
                return <section key={select.id} className={styles["select-field-section"]}>
                    <h2>Select a {select.type}</h2>
                    <Select className={styles["select-field"]}
                        onChange={(selectedOption) => handleSelect(index, selectedOption)}
                        options={select.options}
                        selectedValue={{ value: '', label: '' }}
                    />
                </section>
            })
            }
        </section>
        <section className={styles["display-section"]}>
            <section className={styles["section-toc"]}>
                <h2>Table of content</h2>
                <div className={styles["ul-toc"]}>
                    <ul>
                        {summary !== null ? summary.map(node => <Summary key={node.uri} node={node} currentBook={currentBook} setChange={setChange} setCurrentBook={setCurrentBook} />) : ''}
                    </ul>
                </div>

            </section>
            {sections}
        </section>
    </section>
}

export default DisplayTextComponent;