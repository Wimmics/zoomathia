import { useState, useCallback, useRef, useEffect } from "react";
import SectionComponent from './SectionComponent'
import Select from 'react-select'
import styles from "./css_modules/BookComponents.module.css"
import ParagraphDisplay from "./ParagraphComponent";

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const Summary = ({ node }) => {
    const [uri, setURI] = useState(node.uri)
    return <li id={node.type + "_" + node.id + "_summary"} key={node.type + "_" + node.id}>
        <button onClick={() => {
            const element = document.getElementById(uri)
            if (element && node.type !== "http://www.zoomathia.com/2024/zoo#Paragraph") {
                element.scrollIntoView({ behaviour: 'smooth' })
            } else {
                element.scrollIntoView({ behaviour: 'smooth', block: 'center' })
            }
        }}>{getTypeFromURI(node?.type)} - {node.title !== '' ? node.title : node.id}</button>
        {node.children && node.children.length > 0 && (<ul>
            {node.children.map(child => <Summary key={`${node.type}_${node.id}_summary`} node={child} />)}
        </ul>)}
    </li>
}

const DisplayTextComponent = ({ controller, uri, options, type }) => {
    const [sections, setSections] = useState([])
    const [selectInput, setSelectInput] = useState([])
    const [metadata, setMetadata] = useState({})
    const [summary, setSummary] = useState(null)
    const controllerRef = useRef(controller.current)

    const [currentLang, setCurrentLang] = useState('en')

    const searchConcepts = async (input) => {
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
    }

    const getParagraph = async (e, signal) => {

        const data = await fetch(
            `${process.env.REACT_APP_BACKEND_URL}getParagraphAlone?uri=${e.value}`,
            { signal }
        ).then(response => response.json())

        const para = []
        for (const elt of data) {
            para.push(<ParagraphDisplay
                key={elt.id}
                id={elt.id}
                text={elt.text}
                uri={elt.uri}
                lang={"en"}
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

    useEffect(() => {
        const getMetadata = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getMetadata?uri=${uri}`)
                .then(response => response.json())
            setMetadata(data)
        }

        const getSummary = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getSummary?uri=${uri}`)
                .then(response => response.json())
            setSummary(data[0])
            console.log(data)
        }
        const update = async () => {
            setSelectInput([{ id: 0, type: type, options: options }])
        }

        update()
        getMetadata()
        getSummary()
    }, [options, type])

    return <section>
        <section className={styles["metadata-section"]}>
            <div>
                <h3>Author</h3>
                <p>{metadata.author}</p>
            </div>
            <div>
                <h3>Editor</h3>
                <p>{metadata.editor}</p>
            </div>
            <div>
                <h3>Date</h3>
                <p>{metadata.date}</p>
            </div>
            <div>
                <h3>File</h3>
                <p>{metadata.file}</p>
            </div>
        </section>
        <header className={styles["selection-section"]}>
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
        </header>
        <section className={styles["display-section"]}>
            <div>
                <h2>Summary</h2>
                <ul>
                    {summary !== null ? <Summary node={summary} /> : ''}
                </ul>
            </div>
            {sections}
        </section>


    </section>
}

export default DisplayTextComponent;