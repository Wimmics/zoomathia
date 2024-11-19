import styles from "./Home.module.css"
const Home = () => {
    return <section className={styles["box-content"]}>
        <section className={styles["home-project"]}>
            <h2>About the Application</h2>
            <p>This application is being developed within the framework of the <a target="_blank" rel="noreferrer" href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/hisinum">HisINum project</a> funded by the <a href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux" rel="noreferrer" target="_blank">Academy of Excellence 5</a> of <a href="https://univ-cotedazur.fr/recherche-innovation/defis-scientifiques-idex" rel="noreferrer" target="_blank">IdEx UCA JEDI</a>.</p>
            <p>It aims to support the study of the transmission of zoological knowledge
                from antiquity to the Middle Ages through the analysis of a corpus of
                texts on animals compiled within the framework of the <a href="https://www.cepam.cnrs.fr/sites/zoomathia/presentation-generale-du-gdri-zoomathia/" target="_blank" rel="noreferrer" >Zoomathia GDRI</a> funded by the CNRS.<br /><br /></p>
            <p>It allows:</p>
            <ul className={styles["list-items"]}>
                <li>exploration of the corpus, via a search for works by concept;</li>
                <li>exploration of a selected work from the corpus, with
                visualisation of the concepts annotating each of its parts;</li>
                <li>visualisation of the results of queries implementing
                competency questions on a selected work from the corpus.</li>
            </ul>

            <p>It relies on the exploitation of a knowledge graph annotating the
            Zoomathia corpus of texts with concepts from the <a href="https://opentheso.huma-num.fr/opentheso/?idt=th310" rel="noreferrer" target="_blank">TheZoo thesaurus</a>.</p>
            <p>The pipeline for the automatic construction of this knowledge graph was
            developed within the framework of the <a href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/automazoo-annotation-automatique-dun-corpus-zoologique-ancien" rel="noreferrer" target="_blank">AutomaZoo project</a> funded by the
            Academy of Excellence 5 of IdEx UCA JEDI, and further refined within the
            framework of the HisINum project.</p>
            <p>GitHub of the project: <a href="https://github.com/Wimmics/zoomathia" rel="noreferrer" target="_blank">https://github.com/Wimmics/zoomathia</a></p>
            <p>Access to the knowledge graph through its SPARQL endpoint:
            <a href="http://zoomathia.i3s.unice.fr/sparql" rel="noreferrer" target="_blank">http://zoomathia.i3s.unice.fr/sparql</a><br /><br /><br /></p>
            <p>Contact: <a href="mailto:faro@i3s.unice.fr">Catherine Faron</a></p>
            
        </section>
    </section>
}

export default Home;