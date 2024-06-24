import { useState, useCallback, useRef, useLayoutEffect } from "react";
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
    const [firstLevel, setFirstLevel] = useState([])
    const [secondLevel, setSecondLevel] = useState([])
    const [thirdLevel, setThirdLevel] = useState([])
    const [paragraphSelect, setParagraphSelect] = useState([])
    const controllerRef = useRef(controller.current)

    const [currentLang, setCurrentLang] = useState('en')

    const getChildPart = useCallback((e) => {
        setSections([])
        const uri = e.value
        const title = e.label
        setSections(<SectionComponent sectionTitle={title} uri={uri} controller={controllerRef} />)
    }, [controllerRef])

    const getParagraph = useCallback((e) => {
        const signal = controllerRef.current.signal

        const callForData = async () => {
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
            setSections(para)
        }
        callForData()
    }, [])

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

    const handleSelect = useCallback((e) => {
        if (controllerRef.current) {
            controllerRef.current.abort()
        }
        controllerRef.current = new AbortController()
        const signal = controllerRef.current.signal

        const callForData = async () => {
            let childType = ''
            const checkType = await fetch(
                `${process.env.REACT_APP_BACKEND_URL}getChildrenType?uri=${e.value}`,
            ).then(response => response.json())

            for (const elt of checkType) {
                childType = getTypeFromURI(elt)
            }

            const childOptions = []
            const data = await fetch(
                `${process.env.REACT_APP_BACKEND_URL}getChildren?uri=${e.value}`,
                { signal }
            ).then(response => response.json())

            for (const elt of data) {
                childOptions.push({
                    label: elt.title,
                    value: elt.uri,
                    type: elt.type
                })
            }
            console.log(e.type)
            if (getTypeFromURI(e.type) === 'Paragraph') {
                getParagraph(e)

            } else {

                switch (childType) {
                    case 'Chapter':
                        setSecondLevel(<section className={styles["select-field-section"]}>
                            <h2>Select a Chapter</h2>
                            <Select className={styles["select-field"]} onChange={handleSelect} options={childOptions} selectedValue={null} />
                        </section>)
                        getChildPart(e)
                        break;
                    case 'Section':
                        setThirdLevel(<section className={styles["select-field-section"]}>
                            <h2>Select a Section</h2>
                            <Select className={styles["select-field"]} onChange={handleSelect} options={childOptions} selectedValue={null} />
                        </section>)
                        getChildPart(e)
                        break;
                    case 'Paragraph':
                        setParagraphSelect(<section className={styles["select-field-section"]}>
                            <h2>Select a Paragraph</h2>
                            <Select className={styles["select-field"]} onChange={handleSelect} options={childOptions} selectedValue={null} />
                        </section>)
                        getChildPart(e)
                        break;
                    default:
                        console.log("This type is not currently supported to be display", childType)
                }
            }
        }
        callForData()

        // Start to print Text based on the URI selected
        // Display another selection (paragraph, section etc)
        // Would be easier if current type of uri is stored in selection
    }, [controller, getChildPart, setSecondLevel, setParagraphSelect, setThirdLevel])

    useLayoutEffect(() => {
        switch (type) {
            case 'Paragraph':
                setParagraphSelect(<section className={styles["select-field-section"]}>
                    <h2>Select a Paragraph</h2>
                    <Select className={styles["select-field"]} onChange={handleSelect} options={options} selectedValue={{ value: '', label: '' }} />
                </section>)
                break;
            default:
                setFirstLevel(<section className={styles["select-field-section"]}>
                    <h2>Select a {type}</h2>
                    <Select className={styles["select-field"]} onChange={handleSelect} options={options} selectedValue={{ value: '', label: '' }} />
                </section>)
                break;
        }
    }, [handleSelect, options, type])

    return <section>
        <header className={styles["selection-section"]}>
            {firstLevel}
            {secondLevel}
            {thirdLevel}
            {paragraphSelect}
        </header>
        {sections}

    </section>
}

export default DisplayTextComponent;