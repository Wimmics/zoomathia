import styles from "./About.module.css"
import { NavLink } from 'react-router-dom'

const About = () => {
    return <section className={styles["box-content"]}>
        <section className={styles["home-project"]}>

            <h2>About the Application</h2>

            <p>This application is being developed within the framework of the <a target="_blank" rel="noreferrer" href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/hisinum">HisINum project</a> funded by the <a href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux" rel="noreferrer" target="_blank">Academy of Excellence 5</a> of <a href="https://univ-cotedazur.fr/recherche-innovation/defis-scientifiques-idex" rel="noreferrer" target="_blank">IdEx UCA JEDI</a>. It aims to support the study of the transmission of zoological knowledge from antiquity to the Middle Ages through the analysis of a corpus of texts on animals compiled within the framework of the <a href="https://www.cepam.cnrs.fr/sites/zoomathia/presentation-generale-du-gdri-zoomathia/" target="_blank" rel="noreferrer">Zoomathia GDRI</a> funded by the CNRS.</p>

            <h3 className={styles["section-title"]}>What it allows</h3>
           <div className={styles["cards"]}>
    <NavLink to='/ExploreTheCorpus' className={styles["card"]}>
        <h4>Explore the corpus</h4>
        <p>Search for works by concept across the entire zoological corpus.</p>
    </NavLink>
    <NavLink to='/ExploreAWork' className={styles["card"]}>
        <h4>Explore a work</h4>
        <p>Browse a selected work and visualise the concepts annotating each of its parts.</p>
    </NavLink>
    <NavLink to='/CompetencyQuestion' className={styles["card"]}>
        <h4>Competency questions</h4>
        <p>Visualise the results of queries implementing competency questions on the corpus.</p>
    </NavLink>
</div>

            <h3 className={styles["section-title"]}>Knowledge graph</h3>
            <p>It relies on the exploitation of a knowledge graph annotating the Zoomathia corpus of texts with concepts from the <a href="https://opentheso.huma-num.fr/opentheso/?idt=th310" rel="noreferrer" target="_blank">TheZoo thesaurus</a>. The pipeline for the automatic construction of this knowledge graph was developed within the framework of the <a href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academies-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/automazoo-annotation-automatique-dun-corpus-zoologique-ancien" rel="noreferrer" target="_blank">AutomaZoo project</a> funded by the Academy of Excellence 5 of IdEx UCA JEDI, and further refined within the framework of the HisINum project.</p>

            <h3 className={styles["section-title"]}>Useful links</h3>
            <div className={styles["links-section"]}>
                <a href="https://github.com/Wimmics/zoomathia" rel="noreferrer" target="_blank">GitHub of the project</a>
                <a href="http://zoomathia.i3s.unice.fr/sparql" rel="noreferrer" target="_blank">SPARQL Endpoint</a>
            </div>

            <h3 className={styles["section-title"]}>Contact</h3>
            <div className={styles["contact-section"]}>
                <a href="mailto:faro@i3s.unice.fr" className={styles["contact-card"]}>
                    <p className={styles["contact-name"]}>Catherine Faron</p>
                    <p className={styles["contact-email"]}>faro@i3s.unice.fr</p>
                </a>
                <a href="mailto:Arnaud.Zucker@univ-cotedazur.fr" className={styles["contact-card"]}>
                    <p className={styles["contact-name"]}>Arnaud Zucker</p>
                    <p className={styles["contact-email"]}>Arnaud.Zucker@univ-cotedazur.fr</p>
                </a>
            </div>

        </section>
    </section>
}

export default About;