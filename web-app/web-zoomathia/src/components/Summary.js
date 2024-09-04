import styles from "./css_modules/BookComponents.module.css"

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}


const Summary = ({ node, currentBook, setChange, setCurrentBook }) => {
    const handleDisplay = () => {
        console.log(node.title)
        /* Check if the current display should be regenerated */
        if (!node.uri.includes(currentBook)) {
            console.log(`not includes currentBook=${currentBook} and node.uri=${node.uri}`)
            if(getTypeFromURI(node.type) === "Book"){
                setCurrentBook(node.uri)
            }
            setChange(node.uri, node.title)
        }
    }

    const handleClick = async () => {

        const element = document.getElementById(node.uri)
        handleDisplay()
        if (!element) {
            console.log(`Cannot select element on URI ${node.uri}`)
        } else if (element && node.type !== "http://www.zoomathia.com/2024/zoo#Paragraph") {
            element.scrollIntoView({ behaviour: 'smooth', block: 'start' })
        } else {
            element.scrollIntoView({ behaviour: 'smooth', block: 'center' })

        }
    }
    return <li id={node.type + "_" + node.id + "_summary"} key={node.uri + "_summary"}>
        <details>
            <summary>
                <button className={styles["button-toc"]} onClick={handleClick}>
                    {getTypeFromURI(node?.type)} - {node.title !== '' ? node.title : node.id}
                </button>
            </summary>
            {node.children && node.children.length > 1 && (<ul>
                {node.children.map(child => <Summary
                    key={`${child.uri}_${node.id}_summary`}
                    node={child}
                    currentBook={currentBook}
                    setChange={setChange} setCurrentBook={setCurrentBook}/>)}
                    
            </ul>)}
        </details>
    </li>
}

export default Summary;