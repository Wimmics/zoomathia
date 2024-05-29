import { useState, useCallback, useEffect, useLayoutEffect } from "react";
import SectionComponent from './SectionComponent'
import Select from 'react-select'
import styles from "./css_modules/BookComponents.module.css"

const DisplayTextComponent = ({ controller, bookList }) => {
    const [books, setBooks] = useState([])
    const [sections, setSections] = useState([])
    const [headerSelect, setHeaderSelect] = useState([])
    const [currentLang, setCurrentLang] = useState('en')
    const [sectionType, setSectionType] = useState('')

    const getChildPart = useCallback((e) => {
        setSections([])

        if (controller.current) {
            controller.current.abort()
        }
        controller.current = new AbortController()

        const uri = e.value
        const title = e.label
        setSections(<SectionComponent sectionTitle={title} uri={uri} controller={controller} />)
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

    const handleSelect = (e) => {
        if (controller.current) {
            controller.current.abort()
        }
        controller.current = new AbortController()

        // Start to print Text based on the URI selected
        getChildPart(e)

        // Display another selection (paragraph, section etc)
        if (headerSelect.length > 1) {
            setHeaderSelect(<section className={styles["select-field-section"]}>
                <h2>Select a {sectionType}</h2>
                <Select className={styles["select-field"]} onChange={handleSelect} options={bookList} selectedValue={{ value: '', label: '' }} />
            </section>)
        }
    }

    useLayoutEffect(() => {
        const callForData = async () => {
            // Get current subject type (book, chapter, section etc)
            const data = await fetch().then(reponse => reponse.json())
        }
        setHeaderSelect(<section className={styles["select-field-section"]}>
            <h2>Select a {sectionType}</h2>
            <Select className={styles["select-field"]} onChange={handleSelect} options={bookList} selectedValue={{ value: '', label: '' }} />
        </section>)
    }, [])

    return <section>
        <header>
            {headerSelect}
        </header>
        {sections}

    </section>
}

export default DisplayTextComponent;