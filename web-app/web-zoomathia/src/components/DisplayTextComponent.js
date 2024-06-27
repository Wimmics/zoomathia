import { useState, useCallback, useRef, useEffect } from "react";
import SectionComponent from './SectionComponent'
import Select from 'react-select'
import styles from "./css_modules/BookComponents.module.css"
import ParagraphDisplay from "./ParagraphComponent";

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const DisplayTextComponent = ({ controller, options, type }) => {
    const [sections, setSections] = useState([])
    const [selectInput, setSelectInput] = useState([])
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
        const update = async () => {
            setSelectInput([{ id: 0, type: type, options: options }])
        }
        update()
    }, [options, type])

    return <section>
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
        {sections}

    </section>
}

export default DisplayTextComponent;