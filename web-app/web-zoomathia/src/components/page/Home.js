import styles from "./Home.module.css"
import vizu from "../css_modules/logo/vizu.png"
import filter from "../css_modules/logo/filter.png"
const Home = () => {
    return <section className={styles["box-content"]}>
        <section className={styles["home-project"]}>
        <h2>About Hisinum project and Zoomathia</h2>
            <p>Further information about Zoomathia can be found on the <a href="https://www.cepam.cnrs.fr/sites/zoomathia/presentation-generale-du-gdri-zoomathia/" target="_blank" rel="noreferrer" >Cepam - Zoomathia project</a> web page.
            Zoomathia is also part of the Hisinum project which be presented at <a target="_blank" rel="noreferrer" href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/hisinum">UCA - Hisinum project</a>.</p>
            <h2>About the Application</h2>
            <p>This interface allows users to explore and visualize texts, in Latin and Ancient Greek,  annotated both manually and automatically. Functionally, the application offers two ways to visualize the texts:
                <a href="/ExploreAWork">(1)</a> within a single work previously selected by the user, and <a href="/ExploreTheCorpus">(2)</a> across the entire annotated corpus or within a custom sub-corpus defined by the user.
            </p>
            <img className={styles["box-img"]} src={filter} alt="filter"/>
            <p>The application also allows users to visualize the results of competency questions expressed by experts. 
                Two types of visualizations are available: (1) a table format using raw SPARQL results, and (2) an interactive graph exploration using the MGExplorer tool.
                Those kind of visualisation can be access through the <a href="/CompetencyQuestion">Competency Questions</a> page.</p>
            <img className={styles["box-img"]} src={vizu} alt="vizualisation"/>
            <p>You can query yourself the knowledge graph with the SPARQL endpoint available at <a href={process.env.REACT_APP_CORESE_URL}>{process.env.REACT_APP_CORESE_URL}</a>.</p>
        </section>
    </section>
}

export default Home;