import { useState, useLayoutEffect } from "react"
import ParagraphDisplay from "./ParagraphComponent"

const SectionComponent = (props) => {
    const sectionTitle = props.sectionTitle
    const [sectionParagraph, setSectionParagraph] = useState([])

    /*for (const paragraph of data) {
        title = paragraph.title
        paras.push(
            <ParagraphDisplay
                key={paragraph.id}
                id={paragraph.id}
                text={paragraph.text}
                uri={paragraph.uri}
                lang={currentLang}
                controller={controller.current.signal}
            />
        )
    }*/

    useLayoutEffect(() => {
        setSectionParagraph([])
        const callForData = async () => {
            const signal = props.controller.current.signal
            try {
                const checkType = await fetch(
                    `${process.env.REACT_APP_BACKEND_URL}getChildrenType?uri=${props.uri}`,
                    { signal }
                ).then(response => response.json())
                // Extract only Type part after '#' of Class URI
                const childType = checkType[0].split("#")
                if (childType[childType.length - 1] === "Paragraph") {
                    const paragraphs = []
                    const data = await fetch(
                        `${process.env.REACT_APP_BACKEND_URL}getParagraphs?uri=${props.uri}`,
                        { signal }
                    ).then(response => response.json())
                    for (const elt of data) {
                        paragraphs.push(<ParagraphDisplay
                            key={elt.id}
                            id={elt.id}
                            text={elt.text}
                            uri={elt.uri}
                            lang={"en"}
                            controller={props.controller} />)
                    }
                    setSectionParagraph(paragraphs)

                } else {
                    console.log(signal)
                    // Autant de Section que d'enfant pour cette section
                    const sections = []
                    const children = await fetch(
                        `${process.env.REACT_APP_BACKEND_URL}getChildren?uri=${props.uri}`,
                        { signal }
                    ).then(response => response.json())
                    //setSections(<SectionComponent sectionTitle={title} uri={uri} controller={controller.current} />)
                    for (const elt of children) {
                        sections.push(<SectionComponent uri={elt.uri} sectionTitle={elt.title} controller={props.controller} />)
                    }
                    console.log(childType[childType.length - 1])
                    setSectionParagraph(sections)
                }
            } catch (e) {
                console.log(e)
            }

        }
        callForData()
    }, [props])

    return <section>
        <h2>{sectionTitle}</h2>
        {sectionParagraph}
    </section>

}

export default SectionComponent