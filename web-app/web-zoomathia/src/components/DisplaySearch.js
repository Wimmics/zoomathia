

import Grid from '@mui/material/Grid2';
import ParagraphDisplay from "./ParagraphComponent";

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const DisplaySearch = ({ node }) => {
    
    return <>{((node?.children.length > 0) && ('type' in node?.children[0]))? <> 
            <Grid key={node.uri} id={node.uri} size={12}>
                <h2>{node.title}</h2>
            </Grid> 
            {node?.children.map(n => <DisplaySearch node={n} />)}
        </> :  <>
            {(!('type' in node.children[0]) && node.children.length > 1)
            ? <><Grid key={node.uri} id={node.uri} size={12}>
                <h2>{getTypeFromURI(node.type)} {node.title}</h2>
                {node.children.map(n => <ParagraphDisplay id={n.id} text={n.text} uri={n.uri} concepts={[]} displayId={true} />)}
                </Grid>
            </>
            : <><Grid key={node.uri} id={node.uri} size={12}>
                    <h2>{getTypeFromURI(node.type)} {node.title}</h2>
                </Grid>
                {node.children.map(n => <ParagraphDisplay id={n.id} text={n.text} uri={n.uri} concepts={[]} displayId={false} />)}
            </>
            } 
        </>
        }
    </>
}

export default DisplaySearch