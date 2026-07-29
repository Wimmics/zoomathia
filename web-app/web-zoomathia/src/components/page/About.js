import styles from "./About.module.css"


const About = () => {
    return <section className={styles["box-content"]}>
        <section className={styles["home-project"]}>

            <h2>About the Application</h2>

            <p>This application enables the exploration of a knowledge graph annotating a corpus of Ancient and Medieval texts on Animals (original texts in Ancient Greek and Latin and their translations in English). It aims to support the study of the transmission of zoological knowledge from Antiquity to the Middle Ages.</p>

            <h3 className={styles["section-title"]}>Knowledge graph</h3>
            <p>It relies on the exploitation of a knowledge graph annotating the Zoomathia corpus of texts with concepts from the <a href="https://opentheso.huma-num.fr/opentheso/?idt=th310" rel="noreferrer" target="_blank">TheZoo thesaurus</a>. The pipeline for the automatic construction of this knowledge graph was developed within the framework of the <a href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academies-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/automazoo-annotation-automatique-dun-corpus-zoologique-ancien" rel="noreferrer" target="_blank">AutomaZoo project</a> funded by the Academy of Excellence 5 of IdEx UCA JEDI, and further refined within the framework of the HisINum project.</p>

            <h3 className={styles["section-title"]}>Useful links</h3>
            <div className={styles["links-section"]}>
                <a href="https://github.com/Wimmics/zoomathia" rel="noreferrer" target="_blank">GitHub of the project</a>
                <a href="http://zoomathia.i3s.unice.fr/sparql" rel="noreferrer" target="_blank">SPARQL endpoint to query the Knowledge Graph</a>
                <a href="https://opentheso.huma-num.fr/opentheso/?idt=th310" rel="noreferrer" target="_blank">TheZoo Thesaurus</a>
            </div>

            <h3 className={styles["section-title"]}>Funding</h3>
            <p>This application was developped within the framework of the <a target="_blank" rel="noreferrer" href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/hisinum">AutomaZoo and Hisinum projects</a>, funded by the <a href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux" rel="noreferrer" target="_blank">Academy of Excellence 5</a> of <a href="https://univ-cotedazur.fr/recherche-innovation/defis-scientifiques-idex" rel="noreferrer" target="_blank">Idex UCA JEDI</a>.</p>
            <p>The corpus of texts was compiled in relation with the <a href="https://www.cepam.cnrs.fr/sites/zoomathia/presentation-generale-du-gdri-zoomathia/" target="_blank" rel="noreferrer">Zoomathia international research network</a> funded by CNRS.</p>

            <h3 className={styles["section-title"]}>Contact</h3>
            <div className={styles["contact-section"]}>
                <a href="mailto:catherine.faron@univ-cotedazur.fr" className={styles["contact-card"]}>
                    <p className={styles["contact-name"]}>Catherine Faron</p>
                    <p className={styles["contact-email"]}>catherine.faron@inria.fr</p>
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