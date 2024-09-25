import { useState, useCallback, useEffect } from "react"
import styles from "./css_modules/ParagraphComponent.module.css"

const ListElement = ({uri, label, offsets, onMouseEnter, onMouseLeave, onClick}) => {

    return <li onMouseEnter={() => onMouseEnter(offsets)} onMouseLeave={onMouseLeave} onClick={() => {onClick(uri)}}>
        {label}
    </li>

}

const ParagraphDisplay = ({ id, text, uri, lang, concepts, controller, displayId }) => {
    const [text_content, setTextContent] = useState(<p key={`content-${id}`}>{text}</p>)
    const [conceptsDiv, setConceptsDiv] = useState([])

    const redirectToOpenTheso = (e) => {
        window.open(e, "_blank")
    }

    /*const mergeOffsets = (offsets) => {
        console.log(offsets)
        // Trier les offsets par leur position de départ (et par la position de fin en cas d'égalité)
        offsets.sort((a, b) => a.start - b.start || a.start - b.start);
        
        const merged = [];
        let current = null;
      
        offsets.forEach(offset => {
          if (!current || offset> current) {
            // Aucun chevauchement ou nouvelle plage
            current = { ...offset };
            merged.push(current);
          } else {
            // Chevauchement ou imbrication, fusionner les plages
            current.end = Math.max(current.end, offset.end);
          }
        });
      
        return merged;
      };*/

    const highlight = useCallback((offsets) => {
        /*const parts = [];
        let lastIndex = 0;

        console.log(Math.min(...offsets.map(e => parseInt(e.start))))
        offsets.forEach((offset, index) => {
            const { start, end } = offset;
            // Ajouter le texte avant le span
            parts.push(text.slice(lastIndex, start));
            // Ajouter le texte entouré par le span
            parts.push(<span key={index} className={styles["highlight"]}>{text.slice(start, end)}</span>);
            lastIndex = end;
        });

        // Ajouter le texte restant après le dernier span
        parts.push(text.slice(lastIndex));
        setTextContent(<p key={`content-${id}`}>{parts}</p>);*/
        setTextContent(<p key={`content-${id}`}>{text.slice(0, offsets[0].start)}<span className={styles["highlight"]}>{text.slice(offsets[0].start, offsets[0].end)}</span>{text.slice(offsets[0].end, text.length)}</p>)
        
    }, [text, id])

    const removeHighlight = useCallback((e) => {
        setTextContent(<p key={`content-${id}`}>{text}</p>)
    }, [id, text])

    useEffect(() => {
        const getConcepts = async () => {
            try {

            const concepts = await fetch(
                `${process.env.REACT_APP_BACKEND_URL}getConcepts?uri=${uri}&lang=${"en"}`).then(response => response.json())
            const concepts_list = []

            for(const annotation of  Object.keys(concepts)){
                const offsets = concepts[annotation].offset
                concepts_list.push(
                <ListElement key={`concept_element_${concepts[annotation].label}${lang}`}
                    uri={concepts[annotation].concept}
                    label={concepts[annotation].label}
                    offsets={offsets}
                    onMouseEnter={highlight}
                    onMouseLeave={removeHighlight}
                    onClick={redirectToOpenTheso} />
                )
            }

            setConceptsDiv(<div key={`concept-${id}`} className={styles['concept-list']}>
                <p>{Object.keys(concepts_list).length} concept{Object.keys(concepts_list).length > 1 ? 's' : ''}</p>
                <ul key={`concept-list-${id}`}>
                  {concepts_list}  
                </ul>
            </div>)
        }catch(err){
        console.log(err)
        }
    }

        getConcepts()
    }, [highlight, id, lang, removeHighlight, uri])

    return <section key={`paragraph-section-${id}`} className={styles["paragraph-section"]}>
        <div key={`paragraph-${id}`} id={uri} className={styles["id-paragraph"]}>
            {displayId ? 
                    <>{(uri.includes('http://www.zoomathia.com/Pliny/historia_naturalis')) ? 
                        <p key={`number-${id}`}>{`[${parseInt(id)}]`}</p>  : 
                        <p key={`number-${id}`}>{`[${parseInt(id) + 1}]`}</p>}
                    </> : 
                    <>{(uri.includes('http://www.zoomathia.com/Pliny/historia_naturalis')) ? 
                        <p key={`number-${id}`}>{`[${parseInt(id)}]`}</p>  : 
                        <p key={`number-${id}`}></p>}</>}
        </div>
        <div key={`text-${id}`} className={styles["text-paragraph"]}>
            {text_content}
        </div>
        {conceptsDiv}
    </section>
}

export default ParagraphDisplay;