import { useState, useLayoutEffect } from "react"
import ParagraphDisplay from "./ParagraphComponent"
import styles from "./css_modules/BookComponents.module.css"

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const LOADING_STATE = <>
    <div className={styles["loader"]}></div>
    <p>Loading work...</p>
</>

const SectionComponent = (props) => {
    const sectionTitle = props.sectionTitle
    const [sectionParagraph, setSectionParagraph] = useState(LOADING_STATE)
    const [type, setType] = useState("")

    useLayoutEffect(() => {
        setSectionParagraph([])
        const callForData = async () => {
            const signal = props.controller.current.signal
            try {

                const currentType = await fetch(`${process.env.REACT_APP_BACKEND_URL}getCurrentType?uri=${props.uri}`,
                    { signal }
                ).then(response => response.json())
                let sectionType = ""
                for (const elt of currentType) {
                    sectionType = elt.type
                }
                setType(getTypeFromURI(sectionType))

                const checkType = await fetch(
                    `${process.env.REACT_APP_BACKEND_URL}getChildrenType?uri=${props.uri}`,
                    { signal }
                ).then(response => response.json())
                // Extract only Type part after '#' of Class URI
                const childType = getTypeFromURI(checkType[0])
                if (childType === "Paragraph") {
                    const paragraphs = []
                    const data = await fetch(
                        `${process.env.REACT_APP_BACKEND_URL}getParagraphs?uri=${props.uri}`,
                        { signal }
                    ).then(response => response.json())
                    for (const elt of data) {

                        const concepts_list = await fetch(
                            `${process.env.REACT_APP_BACKEND_URL}getConcepts?uri=${elt.uri}&lang=${"en"}`,
                            { signal }
                        ).then(response => response.json())

                        paragraphs.push(<ParagraphDisplay
                            key={elt.uri}
                            id={elt.id}
                            text={elt.text}
                            uri={elt.uri}
                            lang={"en"}
                            concepts={concepts_list}
                            controller={props.controller} />)
                    }
                    setSectionParagraph(paragraphs)

                } else {
                    const sections = []
                    const children = await fetch(
                        `${process.env.REACT_APP_BACKEND_URL}getChildren?uri=${props.uri}`,
                        { signal }
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

    return <section id={props.uri} key={props.uri}>
        <h2 className={styles["sticky-title"]}>{type} - {sectionTitle}</h2>
        {sectionParagraph}
    </section>

}

export default SectionComponent