

import Grid from '@mui/material/Grid2';
import ParagraphDisplay from "./ParagraphComponent";
import redirection from "./css_modules/logo/redirect-svgrepo-com.svg"
import styles from "./css_modules/ParagraphComponent.module.css"

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const DisplaySearch = ({ node, controller }) => {
    return <>{((node?.children.length > 0) && ('type' in node?.children[0]))? <> 
            <Grid key={node.uri} id={node.uri} size={12}>
                <h2>
                    {node?.type !== undefined ?  <i>{getTypeFromURI(node?.type)}</i>  : console.log(node)} {node.title}
                    <a href={`${process.env.REACT_APP_FRONTEND_URL}ExploreAWork?uri=${node.uri}`} rel="noreferrer" target="_blank">
                        <img className={styles["logo-redirect"]} src={redirection} alt=""/>
                    </a>
                </h2>
                
            </Grid> 
            {node?.children.map(n => <DisplaySearch node={n} controller={controller} />)}
        </> :  <>
            {(node.children.length > 1 && !('type' in node.children[0]))
            ? <><Grid key={node.uri} id={node.uri} size={12}>
                <h2>
                    {node?.type !== undefined ?  <i>{getTypeFromURI(node?.type)}</i>  : console.log(node)} {node.title}
                    <a href={`${process.env.REACT_APP_FRONTEND_URL}ExploreAWork?uri=${node.uri}`} rel="noreferrer" target="_blank">
                        <img className={styles["logo-redirect"]} src={redirection} alt=""/>
                    </a>
                </h2>
                {node.children.map(n => <ParagraphDisplay id={n.id} text={n.text} uri={n.uri} concepts={[]} displayId={true} controller={controller} redirect={true}/>)}
                </Grid>
            </>
            : <><Grid key={node.uri} id={node.uri} size={12}>
                    <h2>
                    {node?.type !== undefined ?  <i>{getTypeFromURI(node?.type)}</i>  : console.log(node)} {node.title}
                    <a href={`${process.env.REACT_APP_FRONTEND_URL}ExploreAWork?uri=${node.uri}`} rel="noreferrer" target="_blank">
                        <img className={styles["logo-redirect"]} src={redirection} alt=""/>
                    </a>
                </h2>
                </Grid>
                {node.children.map(n => <ParagraphDisplay id={n.id} text={n.text} uri={n.uri} concepts={[]} displayId={false} controller={controller} redirect={true}/>)}
            </>
            } 
        </>
        }
    </>
}

export default DisplaySearch