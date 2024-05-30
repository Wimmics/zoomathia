import { useLayoutEffect, useState, useCallback, useRef } from 'react'
import styles from "./css_modules/BookComponents.module.css"
//import DisplayTextComponent from './DisplayTextComponent'
import Select from 'react-select'
import DisplayTextComponent from './DisplayTextComponent'

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const ExplorerComponent = () => {

    const [displayTextComponent, setDisplayTextComponent] = useState(<p>No text selected</p>)

    const [authorList, setAuthorList] = useState([])
    const [worksList, setWorks] = useState([]);

    const [author, setAuthor] = useState('')
    const [work, setWork] = useState('')
    const [title, setTitle] = useState('')

    const controller = useRef(new AbortController())

    const getDisplayText = useCallback((e) => {

        setWork({ label: e.label, value: e.value })
        setDisplayTextComponent(<p>No text selected</p>)

        if (author.label !== e.author) {
            setAuthor({ label: e.author, value: e.value })

        }

        setTitle(`${e.author} - ${e.label}`)

        if (controller.current) {
            controller.current.abort("Canceling Fetch: Work has changed...")
        }
        controller.current = new AbortController()

        const callForData = async () => {
            let bookList = [{ value: '', label: '' }];
            let type = ''

            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getBookList?title=${e.value}`
            ).then(response => response.json())
            for (const book of data) {
                type = getTypeFromURI(book.type)
                bookList.push({ value: book.uri, label: book.title, id: book.id, number: book.id, type: getTypeFromURI(book.type) })
            }

            setDisplayTextComponent(
                <DisplayTextComponent className={styles["select-field"]}
                    controller={controller}
                    options={bookList}
                    type={type} />)
        }

        callForData()
    }, [author])

    const getWorks = useCallback((e) => {
        const workList = [{ label: '', value: '' }]
        let urlRequest = `${process.env.REACT_APP_BACKEND_URL}getWorksFromAuthors?author=${e.value}`

        if (controller.current) {
            controller.current.abort("Canceling Fetch: Author has changed...")
        }
        controller.current = new AbortController()

        const callForData = async () => {
            setWorks([{ label: '', value: '' }])
            setTitle('')
            setDisplayTextComponent(<p>No text selected</p>)
            if (e.value === '') {
                urlRequest = `${process.env.REACT_APP_BACKEND_URL}getWorks`
            }

            const data = await fetch(urlRequest)
                .then(response => response.json())
                .catch(e => { console.log(e) })
            for (const work of data) {
                workList.push({ value: work.uri, label: work.title, author: work.author })
            }
            setWorks(workList) // Set select options list
            setWork(null) // Clear value of select input
            setAuthor({ label: e.label, value: e.value }) // Set current value of author
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
                <Select id="work-select" className={styles["select-field"]} onChange={getDisplayText} options={worksList} value={work} selectedValue={work} />
            </section>
        </header>


        <header className={styles["selected-book-title"]}>
            <h2>{title}</h2>
        </header>

        {displayTextComponent}

    </div>
}

export default ExplorerComponent;


