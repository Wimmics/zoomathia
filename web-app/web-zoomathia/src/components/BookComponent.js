import { useLayoutEffect, useState, useCallback, useRef } from 'react'
import styles from "./css_modules/BookComponents.module.css"
import ParagraphDisplay from './ParagraphComponent'
import SelectComponent from './SelectComponent'
import Select from 'react-select'
import SectionComponent from './SectionComponent'

const BookPage = () => {

    const [books, setBooks] = useState([])
    const [sections, setSections] = useState([])
    const [title, setTitle] = useState()
    const [authorList, setAuthorList] = useState([])
    const [works, setWorks] = useState([]);
    const [currentLang, setCurrentLang] = useState('en')
    const controller = useRef(null)

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

    const postParagraphWithConcepts = ''/*useCallback((e) => {
        const callForData = async (e) => {
            const paras = []
            const data = await fetch(
                `${process.env.REACT_APP_BACKEND_URL}getParagraphWithConcept`,
                {
                    method: 'POST',
                    headers: { 'content-type': 'application/json' },
                    body: JSON.stringify({ uri: currentBookUri, concepts: e },),
                    signal: controller.signal
                }).then(response => response.json())

            for (const paragraph of data) {
                paras.push(<ParagraphDisplay
                    key={paragraph.id}
                    id={paragraph.id}
                    text={paragraph.text}
                    uri={paragraph.uri}
                    lang={currentLang}
                    controller={controller.current.signal} />)
            }

            if (paras.length === 0) {
                setSections(<p className={styles["no-result"]}>No paragraphs</p>)
            } else {
                setSections([])
                setSections(paras)
            }

        }
        try {
            callForData(e)
        } catch (e) {
            if (e.name === "AbortError") {
                console.log("Fetch has been canceled")
            } else {
                console.error("Fetch error", e)
            }
        }
    }, [currentLang, setSections])*/

    const searchConcepts = async (input) => {
        const retrieved_concept = []
        const callForData = async (input) => {
            if (input === '') {
                return []
            } else {
                const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}searchConcepts?input=${input}&lang=${currentLang}`).then(response => response.json())
                for (const concept of data) {
                    retrieved_concept.push({ value: concept.uri, label: `${concept.label}@${currentLang}` })
                }
                return retrieved_concept
            }
        }
        return await callForData(input)
    }

    const getBookList = useCallback((e) => {
        let bookList = [{ value: '', label: '' }];
        setBooks([])
        if (controller.current) {
            controller.current.abort("Canceling Fetch: Work has changed...")
        }
        controller.current = new AbortController()

        const callForData = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getBookList?title=${e.value}`
            ).then(response => response.json())
            for (const book of data) {
                bookList.push({ value: book.uri, label: book.title, id: book.id, number: book.id })
            }

            setBooks(<section>
                <h2 key="book">Select book</h2>
                <Select className={styles["select-field"]} onChange={getChildPart} options={bookList} selectedValue={{ value: '', label: '' }} />
            </section>)
            setTitle(`${e.author} - ${e.label}`)
        }

        callForData()
    }, [getChildPart])

    const getWorks = useCallback((e) => {
        const workList = [{ value: '', label: '' }]
        if (controller.current) {
            controller.current.abort("Canceling Fetch: Author has changed...")
        }
        controller.current = new AbortController()

        const callForData = async () => {
            setWorks([])
            setBooks([])
            // TODO: Cancel every fetch action
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getWorks?author=${e.value}`
            ).then(response => response.json())
                .catch(e => {

                })
            for (const work of data) {
                workList.push({ value: work.uri, label: work.title, author: work.author })
            }
            setWorks(<section key="work">
                <h2 key="work">Work</h2>
                <Select className={styles["select-field"]} onChange={getBookList} options={workList} selectedValue={{ value: '', label: '' }} />
            </section>)
        }
        callForData()
        // Cleanup
        return () => {
            controller.current.abort()
        }
    }, [getBookList, controller])



    useLayoutEffect(() => {

        const author_response = [{ value: '', label: '' }]
        const callForData = async () => {
            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getAuthors`
            ).then(response => response.json())
            for (const author of data) {
                author_response.push({ value: author.name, label: author.name })
            }

            setAuthorList(<section key="author" className={styles["author-section"]}>
                <h2 key="author">Author</h2>
                <Select className={styles["select-field"]} onChange={getWorks} options={author_response} selectedValue={{ value: '', label: '' }} />
            </section>)
        }
        callForData()
    }, [getWorks, postParagraphWithConcepts])

    return <div className={styles["box-content"]}>
        <header className={styles["selection-section"]}>
            {authorList}
            {works}
            {books}
        </header>


        <header className={styles["selected-book-title"]}>
            <h2>{title}</h2>
        </header>
        {sections}
    </div>
}
const old = `{currentBookUri !== '' ? <SelectComponent
key={currentBookUri}
execute_effect={postParagraphWithConcepts}
filter_title="Filter paragraph with concept"
load={searchConcepts}
setLanguage={setCurrentLang}
/> : <></>}`

export default BookPage;


