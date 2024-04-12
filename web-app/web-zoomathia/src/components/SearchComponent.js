import styles from "./css_modules/SearchComponent.module.css"
import { useState, useCallback } from "react"
import ParagraphDisplay from './ParagraphComponent'
import SelectComponent from './SelectComponent'

const BookSection = (props) => {
    return <>
        <section className={styles["selected-book-title"]}>
            <h2>{props.title}</h2>
        </section>
        {props.paragraphs}
    </>
}

const SearchComponent = () => {
    const [paragraphs, setParagraphs] = useState([])
    const [currentLang, setCurrentLang] = useState("en")

    const searchConcepts = async (input) => {
        const retrieved_concept = []
        const callForData = async (input) => {
            if (input === '') {
                return []
            } else {
                const data = await fetch(`${process.env.BACKEND_URL}searchConcepts?input=${input}&lang=${currentLang}`).then(response => response.json())
                for (const concept of data) {
                    retrieved_concept.push({ value: concept.uri, label: `${concept.label} @${currentLang}` })
                }
                return retrieved_concept
            }
        }
        return await callForData(input)
    }

    const postParagraphWithConcepts = useCallback((e) => {

        const callForData = async (e) => {
            const paras = []
            const book_found = {}

            const data = await fetch(
                `${process.env.BACKEND_URL}getParagraphsWithConcepts`,
                {
                    method: 'POST',
                    headers: { 'content-type': 'application/json' },
                    body: JSON.stringify({ concepts: e })
                }).then(response => response.json())

            for (const paragraph of data) {
                if (!book_found.hasOwnProperty(paragraph.bookUri)) {
                    book_found[paragraph.bookUri] = {
                        author: paragraph.author,
                        id: paragraph.bookId,
                        paragraphs: [],
                        title: paragraph.title
                    }
                }
                book_found[paragraph.bookUri]['paragraphs'].push(
                    <ParagraphDisplay
                        key={paragraph.id}
                        id={paragraph.id}
                        text={paragraph.text}
                        uri={paragraph.uri}
                        lang={currentLang}
                    />
                )
            }
            for (const key of Object.keys(book_found)) {
                paras.push(
                    <BookSection
                        key={key}
                        paragraphs={book_found[key].paragraphs}
                        uri={key}
                        id={book_found[key]['id']}
                        title={`${book_found[key]['title']} - ${book_found[key]["author"]}`}
                    />
                )
            }
            if (data.length === 0) {
                setParagraphs([])
                setParagraphs(<section className={styles["not-found"]}>
                    <p>No result for concepts label</p>
                </section>
                )
            } else {
                setParagraphs([])
                setParagraphs(paras)
            }
        }
        callForData(e)
    }, [currentLang, setParagraphs])

    return <div className={styles["box-content"]}>
        <section className={styles["search-title"]}>
            <h2>Select concepts</h2>
        </section>
        <SelectComponent
            execute_effect={postParagraphWithConcepts}
            load={searchConcepts}
            filter_title=""
            setLanguage={setCurrentLang}
        />
        {paragraphs}
    </div>

}

export default SearchComponent;