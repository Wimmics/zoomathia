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
    const [worksList, setWorks] = useState([]);
    const [author, setAuthor] = useState('')
    const [work, setWork] = useState('')
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

    const getBook = useCallback((e) => {
        let bookList = [{ value: '', label: '' }];
        setBooks([])
        if (controller.current) {
            controller.current.abort("Canceling Fetch: Work has changed...")
        }
        controller.current = new AbortController()
        setWork({ label: e.label, value: e.value })

        if (author.label !== e.author) {
            setAuthor({ label: e.author, value: e.value })
        }

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
        const workList = [{ label: '', value: '' }]
        let urlRequest = `${process.env.REACT_APP_BACKEND_URL}getWorksFromAuthors?author=${e.value}`

        if (controller.current) {
            controller.current.abort("Canceling Fetch: Author has changed...")
        }
        controller.current = new AbortController()
        const callForData = async () => {
            setWorks([{ label: '', value: '' }])
            setBooks([])
            if (e.value === '') {
                urlRequest = `${process.env.REACT_APP_BACKEND_URL}getWorks`
            }

            const data = await fetch(urlRequest)
                .then(response => response.json())
                .catch(e => { console.log(e) })
            for (const work of data) {
                workList.push({ value: work.uri, label: work.title, author: work.author })
            }
            setWorks(workList)
            setWork({ label: '', value: '' })
            setAuthor({ label: e.label, value: e.value })
        }
        callForData()


    }, [controller, setAuthor])



    useLayoutEffect(() => {

        const author_response = [{ label: '', value: '' }]
        const work_response = [{ label: '', value: '' }]

        const callForData = async () => {

            const data_author = await fetch(`${process.env.REACT_APP_BACKEND_URL}getAuthors`
            ).then(response => response.json()).catch(e => { console.log(e) })
            for (const author of data_author) {
                author_response.push({ value: author.name, label: author.name })
            }
            setAuthorList(author_response)

            const data_works = await fetch(`${process.env.REACT_APP_BACKEND_URL}getWorks`
            ).then(response => response.json())
                .catch(e => { console.log(e) })
            for (const work of data_works) {
                work_response.push({ value: work.uri, label: work.title, author: work.author })
            }
            setWorks(work_response)
        }

        callForData()
    }, [])

    return <div className={styles["box-content"]}>
        <header className={styles["selection-section"]}>
            <section key="author" className={styles["select-field-section"]}>
                <h2 key="author">Author</h2>
                <Select id="author-select" className={styles["select-field"]} onChange={getWorks} options={authorList} value={author} selectedValue={author} />
            </section>
            <section key="work" className={styles["select-field-section"]}>
                <h2 key="work">Work</h2>
                <Select id="work-select" className={styles["select-field"]} onChange={getBook} options={worksList} value={work} selectedValue={work} />
            </section>
        </header>


        <header className={styles["selected-book-title"]}>
            <h2>{title}</h2>
        </header>

        {books}
        {sections}

    </div>
}

export default BookPage;


