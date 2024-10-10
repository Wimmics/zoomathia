import { TreeItem } from "@mui/x-tree-view"

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}


const removeDuplicate = (node) => {
    return node.filter((obj1, i, arr) => 
        arr.findIndex(obj2 => (obj2.id === obj1.id)) === i
      )
}

const Summary = ({ node, currentBook, setChange, setCurrentBook }) => {

    const handleDisplay = () => {
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
        if(setChange !== null){
            handleDisplay()
        }

        if (!element) {
            console.log(`Cannot select element on URI ${node.uri}`)
        }else if (element) {
            const offsetSvh = 10;
            const offset = (window.innerHeight * offsetSvh) / 100;
            const elementPosition = element.getBoundingClientRect().top + window.scrollY;
            const offsetPosition = elementPosition - offset;
            window.scrollTo({ behaviour: 'smooth', top: offsetPosition})
        }
    }

    return <TreeItem id={node.type + "_" + node.id + "_summary"}  itemId={node?.uri + "_summary"} onClick={handleClick}
                label={ `${node.type ? 
                (getTypeFromURI(node.type) !== "Oeuvre" ? getTypeFromURI(node.type) : node.author) : 'Paragraph'} - ${((node.title && node.title !== '') ? node.title : node.id)}`}>
            {node.children && node.children.length > 1 && (<>
                {removeDuplicate(node.children).map(child => <Summary
                    key={`${child?.uri}_${node.id}_summary`}
                    node={child}
                    currentBook={currentBook}
                    setChange={setChange} setCurrentBook={setCurrentBook}/>)}
                    
                </>)}
    </TreeItem>
}

export default Summary;