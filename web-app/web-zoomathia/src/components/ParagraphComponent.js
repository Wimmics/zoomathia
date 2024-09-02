import { useState, useEffect, useCallback } from "react"
import styles from "./css_modules/ParagraphComponent.module.css"

const ListElement = ({uri, label, offsets, onMouseEnter, onMouseLeave, onClick}) => {

    return <li onMouseEnter={() => onMouseEnter(offsets)} onMouseLeave={onMouseLeave} onClick={() => {onClick(uri)}}>
        {label}
    </li>

}

const ParagraphDisplay = ({ id, text, uri, lang, concepts, controller }) => {
    const [text_content, setTextContent] = useState(<p key={`content-${id}`}>{text}</p>)
    const [nbConcept, setNbConcept] = useState(0)

    const redirectToOpenTheso = (e) => {
        window.open(e, "_blank")
    }


    const mergeOffsets = (offsets) => {
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
      };

    const highlight = useCallback((offsets) => {
        const parts = [];
        let lastIndex = 0;

        // Il faut agrandir quand ça se chevauche et positionner correctement dans le cas contraire

        // Parcourir les offsets triés par la position de départ
        offsets.forEach((offset, index) => {
            const { start, end } = offset;
            if (start > lastIndex) {
            // Ajouter le texte avant le span
                parts.push(text.slice(lastIndex, start));
            }
            // Ajouter le texte entouré par le span
            parts.push(<span key={`${index}-${start}`} className={styles["highlight"]}>{text.slice(start, end)}</span>);
            lastIndex = Math.max(lastIndex, end);
        });

        // Ajouter le texte restant après le dernier span
        if (lastIndex < text.length) {
            parts.push(text.slice(lastIndex));
        }

        /*offsets.forEach((offset, index) => {
            const { start, end } = offset;
            // Ajouter le texte avant le span
            parts.push(text.slice(lastIndex, start));
            // Ajouter le texte entouré par le span
            parts.push(<span key={index} className={styles["highlight"]}>{text.slice(start, end)}</span>);
            lastIndex = end;
        });

        // Ajouter le texte restant après le dernier span
        parts.push(text.slice(lastIndex));
        console.log(parts)*/
        setTextContent(<p key={`content-${id}`}>{parts}</p>);
        
    }, [text, id])

    const removeHighlight = useCallback((e) => {
        setTextContent(<p key={`content-${id}`}>{text}</p>)
    }, [id, text])

    const extractConcept = (concepts) => {
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
            

        return concepts_list
    }

    return <section key={`paragraph-section-${id}`} className={styles["paragraph-section"]}>
        <div key={`paragraph-${id}`} id={uri} className={styles["id-paragraph"]}>
            <p key={`number-${id}`}>[{id}]</p>
        </div>
        <div key={`text-${id}`} className={styles["text-paragraph"]}>
            {text_content}
        </div>
        <div key={`concept-${id}`} className={styles['concept-list']}>
            <p>{Object.keys(concepts).length} concept{Object.keys(concepts).length > 1 ? 's' : ''}</p>
            <ul key={`concept-list-${id}`}>
                {extractConcept(concepts) }
            </ul>
        </div>
    </section>
}

export default ParagraphDisplay;