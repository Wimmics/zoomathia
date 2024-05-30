import { useState, useCallback, useEffect, useLayoutEffect } from "react";
import SectionComponent from './SectionComponent'
import Select from 'react-select'
import styles from "./css_modules/BookComponents.module.css"

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const DisplayTextComponent = ({ controller, options, type }) => {
    const [sections, setSections] = useState([])
    const [bookSelect, setBookSelect] = useState([])
    const [chapterSelect, setChapterSelect] = useState([])
    const [sectionSelect, setSectionSelect] = useState([])
    const [paragraphSelect, setParagraphSelect] = useState([])

    const [currentLang, setCurrentLang] = useState('en')

    const getChildPart = useCallback((e) => {
        setSections([])
        const uri = e.value
        const title = e.label
        setSections(<SectionComponent sectionTitle={title} uri={uri} controller={controller} />)
    }, [controller])

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
        const callForData = async () => {
            console.log(e)
            let childType = ''
            const checkType = await fetch(
                `${process.env.REACT_APP_BACKEND_URL}getChildrenType?uri=${e.value}`,
            ).then(response => response.json())

            for (const elt of checkType) {
                childType = getTypeFromURI(elt)
            }

            if (controller.current) {
                controller.current = new AbortController()
            }
            const signal = controller.current.signal

            console.log(signal)
            const childOptions = []
            const data = await fetch(
                `${process.env.REACT_APP_BACKEND_URL}getChildren?uri=${e.value}`,
                { signal }
            ).then(response => response.json())
            console.log(data)
            for (const elt of data) {
                childOptions.push({
                    label: elt.title,
                    value: elt.uri,
                    type: elt.type
                })
            }

            switch (childType) {
                case 'Chapter':
                    setChapterSelect(<section className={styles["select-field-section"]}>
                        <h2>Select a Chapter</h2>
                        <Select className={styles["select-field"]} onChange={handleSelect} options={childOptions} selectedValue={{ value: '', label: '' }} />
                    </section>)
                    break;
                case 'Section':
                    setSectionSelect(<section className={styles["select-field-section"]}>
                        <h2>Select a Section</h2>
                        <Select className={styles["select-field"]} onChange={handleSelect} options={childOptions} selectedValue={{ value: '', label: '' }} />
                    </section>)
                    break;
                case 'Paragraph':
                    setParagraphSelect(<section className={styles["select-field-section"]}>
                        <h2>Select a Paragraph</h2>
                        <Select className={styles["select-field"]} onChange={handleSelect} options={childOptions} selectedValue={{ value: '', label: '' }} />
                    </section>)
                    break;
                default:
                    console.log("This type is not currently supported to be display", childType)
            }
            getChildPart(e)
        }
        callForData()

        // Start to print Text based on the URI selected
        // Display another selection (paragraph, section etc)
        // Would be easier if current type of uri is stored in selection
    }, [controller, getChildPart, setChapterSelect, setParagraphSelect, setSectionSelect])

    useLayoutEffect(() => {
        switch (type) {
            case 'Book':
                setBookSelect(<section className={styles["select-field-section"]}>
                    <h2>Select a Book</h2>
                    <Select className={styles["select-field"]} onChange={handleSelect} options={options} selectedValue={{ value: '', label: '' }} />
                </section>)
                break;
            case 'Chapter':
                setChapterSelect(<section className={styles["select-field-section"]}>
                    <h2>Select a Chapter</h2>
                    <Select className={styles["select-field"]} onChange={handleSelect} options={options} selectedValue={{ value: '', label: '' }} />
                </section>)
                break;
            case 'Section':
                setSectionSelect(<section className={styles["select-field-section"]}>
                    <h2>Select a Section</h2>
                    <Select className={styles["select-field"]} onChange={handleSelect} options={options} selectedValue={{ value: '', label: '' }} />
                </section>)
                break;
            case 'Paragraph':
                setParagraphSelect(<section className={styles["select-field-section"]}>
                    <h2>Select a Paragraph</h2>
                    <Select className={styles["select-field"]} onChange={handleSelect} options={options} selectedValue={{ value: '', label: '' }} />
                </section>)
                break;
            default:
                console.log(`Unknown type: ${type}`)
        }
    }, [handleSelect, options, type])

    return <section>
        <header className={styles["selection-section"]}>
            {bookSelect}
            {chapterSelect}
            {sectionSelect}
            {paragraphSelect}
        </header>
        {sections}

    </section>
}

export default DisplayTextComponent;