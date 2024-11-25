import { useLayoutEffect, useState, useCallback, useRef } from 'react'
import styles from "./css_modules/BookComponents.module.css"
import Select from 'react-select'
import DisplayTextComponent from './DisplayTextComponent'
import { useSearchParams } from 'react-router-dom';

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const ExplorerComponent = () => {

    const [displayTextComponent, setDisplayTextComponent] = useState(<div>
        <p className={styles["p-start"]}>No text selected</p>
        </div>)
    const [searchParams, setSearchParams] = useSearchParams();
    const [authorList, setAuthorList] = useState([])
    const [worksList, setWorks] = useState([]);

    const [author, setAuthor] = useState(null)
    const [work, setWork] = useState(null)

    const controller = useRef(new AbortController())

    const uri = searchParams.get('uri');

    const loadFromUrl = (uri) => {
        const callForData = async () => {

            if (controller.current) {
                controller.current.abort("Canceling Fetch: Work has changed...")
            }
            controller.current = new AbortController()
            const signal = controller.current.signal
            
            let bookList = [{ value: '', label: '' }];
            let type = ''

            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getWorkPart?title=${uri}`, {signal}
                ).then(response => response.json())

            for (const book of data) {
                type = getTypeFromURI(book.type)
                bookList.push({ value: book.uri, label: book.title, id: book.id, number: book.id, type: getTypeFromURI(book.type) })
            }

            setDisplayTextComponent(
                <DisplayTextComponent className={styles["select-field"]}
                    controller={controller}
                    uri={uri}
                    options={bookList}
                    type={type} />)
        }

        callForData()
    }

    const loadText = useCallback((e) => {
        setSearchParams("")
        if(!author && !work){
            console.log("nothing selected")
            return
        }

        const callForData = async () => {

            if (controller.current) {
                controller.current.abort("Canceling Fetch: Work has changed...")
            }
            controller.current = new AbortController()
            const signal = controller.current.signal
            
            let bookList = [{ value: '', label: '' }];
            let type = ''

            const data = await fetch(`${process.env.REACT_APP_BACKEND_URL}getWorkPart?title=${work.value}`, {signal}
                ).then(response => response.json())

            for (const book of data) {
                type = getTypeFromURI(book.type)
                bookList.push({ value: book.uri, label: book.title, id: book.id, number: book.id, type: getTypeFromURI(book.type) })
            }

            setDisplayTextComponent(
                <DisplayTextComponent className={styles["select-field"]}
                    controller={controller.current}
                    uri={work.value}
                    options={bookList}
                    type={type} />)
        }

        callForData()
    }, [author, work])

    const setWorkAndFilter = useCallback((e) => {

        if(e.label === ''){
            setWork(null)
        }else{
            setWork({ label: e.label, value: e.value })
            if (!author || author?.label !== e.author) {
                setAuthor({ label: e.author, value: e.value })
            }
        }        
    },[author])

    const setAuthorAndFilter = useCallback((e) => {
        const workList = [{ label: '', value: '' }]
        let urlRequest = `${process.env.REACT_APP_BACKEND_URL}getWorksFromAuthors?author=${e.value}`


        const signal = controller.current.signal

        const callForData = async () => {
            setWorks([{ label: '', value: '' }])
            if (e.value === '') {
                urlRequest = `${process.env.REACT_APP_BACKEND_URL}getWorks`
            }

            const data = await fetch(urlRequest, {signal})
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

        const getWorkFromUri = async (uri) => {
            let workUri = ''
            const result = await fetch(`${process.env.REACT_APP_BACKEND_URL}getWorkByUri?uri=${uri}`
            ).then(response => response.json())
            for(const elt of result){
                
                setWork({label: elt.title, value: elt.uri})
                setAuthor({label: elt.author, value: elt.uri})
                workUri = elt.uri
            }

            loadFromUrl(workUri)
        }

        if(uri){
            getWorkFromUri(uri)
        }

    }, [uri])

    const clearInputField = (e) => {
        setSearchParams("")
        if (controller.current) {
            controller.current.abort("Clear input select field and cancel current request")
        }

        controller.current = new AbortController()
        setAuthor(null)
        setWork(null)
        setDisplayTextComponent(<p className={styles["p-start"]}>No text selected</p>)
    }

    return <div id={"box-content"} className={styles["box-content"]}>
        <header className={styles["selection-section"]}>
            <section key="author" className={styles["select-field-section"]}>
                <Select id="author-select" className={styles["select-field"]} placeholder="Select or type an author" onChange={setAuthorAndFilter} options={authorList} value={author} selectedValue={author} />
            </section>
            <section key="work" className={styles["select-field-section"]}>
                <Select id="work-select" className={styles["select-field"]} placeholder="Select or type a work" onChange={setWorkAndFilter} options={worksList} value={work} selectedValue={work} />
            </section>
            <section key="send" className={styles["select-field-section"]}>
                <button className={styles["btn-submit-search"]} onClick={clearInputField}>clear</button>
                <button className={styles["btn-submit-search"]} onClick={loadText}>search</button>
            </section>
        </header>

        {displayTextComponent}

    </div>
}

export default ExplorerComponent;


