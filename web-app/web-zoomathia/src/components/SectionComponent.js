import { useState, useEffect, useRef } from "react"
import ParagraphDisplay from "./ParagraphComponent"
import styles from "./css_modules/BookComponents.module.css"

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}



const SectionComponent = (props) => {
    const sectionTitle = props.sectionTitle
    const controllerRef = useRef(props.controller)
    const [type, setType] = useState("")

    const LOADING_STATE = (e) => <section className={styles["text-part"]}>
            <div className={styles["loader"]}></div>
            <p className={styles["loading-p"]}>Loading data...</p>
            <p className={styles["loading-p"]}>Get concept of {e}</p>
        </section>

    const [sectionParagraph, setSectionParagraph] = useState(LOADING_STATE())

    useEffect(() => {
        setSectionParagraph([])
        const callForData = async () => {
            
            setSectionParagraph(LOADING_STATE)
            try {
                const currentType = await fetch(`${process.env.REACT_APP_BACKEND_URL}getCurrentType?uri=${props.uri}`,
                    {signal: controllerRef.current.signal}
                ).then(response => response.json())
                let sectionType = ""
                for (const elt of currentType) {
                    sectionType = elt.type
                }
                setType(getTypeFromURI(sectionType))

                const checkType = await fetch(
                    `${process.env.REACT_APP_BACKEND_URL}getChildrenType?uri=${props.uri}`,
                    {signal: controllerRef.current.signal}
                ).then(response => response.json())
                // Extract only Type part after '#' of Class URI
                const childType = getTypeFromURI(checkType[0])
                if (childType === "Paragraph") {
                    const paragraphs = []
                    const data = await fetch(
                        `${process.env.REACT_APP_BACKEND_URL}getParagraphs?uri=${props.uri}`,
                        {signal: controllerRef.current.signal}
                    ).then(response => response.json())
                    for (const elt of data) {
                        setSectionParagraph(LOADING_STATE(elt.uri))
                        const concepts_list = await fetch(
                            `${process.env.REACT_APP_BACKEND_URL}getConcepts?uri=${elt.uri}&lang=${"en"}`,
                            {signal: controllerRef.current.signal}
                        ).then(response => response.json())
                        console.log(sectionType)
                        const bekker = sectionType.includes("Bekker") ? true : false

                        paragraphs.push(<ParagraphDisplay
                            key={elt.uri}
                            id={elt.id}
                            text={elt.text}
                            uri={elt.uri}
                            lang={"en"}
                            displayId={data.length > 1 ? true : false}
                            concepts={concepts_list}
                            controller={props.controller}
                            bekker={bekker} />)
                    }
                    setSectionParagraph(paragraphs)

                } else {
                    const sections = []
                    const children = await fetch(
                        `${process.env.REACT_APP_BACKEND_URL}getChildren?uri=${props.uri}`,
                        {signal: controllerRef.current.signal}
                    ).then(response => response.json())
                    for (const elt of children) {
                        sections.push(<SectionComponent key={elt.uri} uri={elt.uri} sectionTitle={elt.title} controller={props.controller} />)
                    }
                    setSectionParagraph(sections)
                }
            } catch (e) {
                console.log(e)
            }

        }
        callForData()
    }, [props])

    return <section id={props.uri} key={props.uri} className={styles["text-part"]}>
        <h2 className={styles["sticky-title"]}>{type} {sectionTitle}</h2>
        {sectionParagraph}
    </section>

}

export default SectionComponent