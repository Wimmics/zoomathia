import styles from "./Home.module.css"
import cloud from "../css_modules/logo/une_img_presentation.jpg"
import hisinum from "../css_modules/logo/hisinum.png"
const Home = () => {
    return <section className={styles["box-content"]}>
        <section className={styles["home-project"]}>
            <h2>About Zoomathia</h2>
            <div className={styles["box-part"]}>            
                <div className={styles["box-text"]}>
                <p>The project ZOOMATHIA aims to study the formation and transmission of ancient zoological knowledge over a long period, with an historical, literary and epistemological approach,
                     through texts and iconography, especially in a pivotal period (late Antiquity and the Early Middle Ages), presenting a large dispersion and a wide range of atypical relay of this knowledge.
                      This project is inspired by the the program « Seminars of history on zoological knowledge » led by Liliane Bodson in Liege from 1989 to 2004.
                       This project is motivated by the lack of research coordination on the area, and aims to establish a synergy of investigations often solitary or focused on very limitated corpus or topics.
                        Generally limitated to a few central figures and lamenting the « disappearance of Aristotle’s biology » (J.G. Lennox), the research on ancient zoology needs a more extensive,
                         synthetic and diachronic approach. The purpose is to build a critical and methodological history of zoological knowledge, enlightening overlooked periods
                          or process of the transmission and social/literary mutation of this knowledge. This diachronic synthesis has to take into account the different dimensions of
                           zoological knowledge (through texts, images and biological data): biology, epistemology, history, philology, archeology, philosophy and technology.
                </p>
                <p>Source: <a href="https://www.cepam.cnrs.fr/sites/zoomathia/presentation-generale-du-gdri-zoomathia/" target="_blank" rel="noreferrer" >Cepam - Zoomathia project</a></p>
                </div>
                <div className={styles["box-img"]}>
                    <img src={cloud} alt="Zoomathia cloud word"/>
                </div>
            </div>
            <h2>About Hisinum project</h2> 
                    <h4>Context</h4>
                    <p>Digital transformation is profoundly impacting researchers' practices in the field of humanities and social sciences (HSS), even to the point of questioning the boundaries of disciplines. Moreover, shared digital tools act as a methodological catalyst between disciplines, suggesting a renewed interdisciplinarity, whether within the HSS or between the HSS and the so-called "hard" sciences. The concept of data in the humanities and social sciences takes on multiple forms, as do the new practices enabled by digital tools. These practices require the acquisition of new skills, but they are also based on the use of shared or similar tools, common databases, and replicable methodologies.</p>
                    <h4>Objectifs</h4>
                    <p>This multidisciplinary and unifying project brings together three teams, four laboratories, and external partners in a structured and open approach to share related, interoperable, and generalizable tools. The aim is to pool skills, tools, and methodological reflections in an initial exploratory phase, leveraging synergies between programs to enhance expertise, disseminate knowledge, and crystallize these learnings. This will foster a sustainable site dynamic through seminars focused on sharing issues and results, as well as through training. The medium-term goal is to apply for calls that fund the acquisition of digital infrastructures or common transdisciplinary research projects.</p>
                    <h4>Interdisciplinarity and partnerships</h4>
                    <p>The aim is to foster collaboration between teams through shared practices, to enhance and exchange expertise by sharing "best practices" (seminars, training), to maintain a dynamic interaction between HSS, digital sciences, and AI, and to disseminate this knowledge within UCA.</p>
            <div className={styles["box-part"]}> 
                <div className={styles["box-img"]}>
                    <img src={hisinum} alt="Hisinum members"/>
                </div>
                <div className={styles["box-text"]}>
                    <h4>Project manager</h4>
                    <p>- <b>Muriel Dal Pont Legrand</b>, professeur des universités en sciences économiques, spécialisée en histoire récente de la pensée économique, GREDEG, EUR ELMI</p>
                    <h4>Consortium partners</h4>
                    <p>- <b>Groupe de recherche en droit, économie et sciences de gestion (GREDEG)</b>, CNRS et EUR ELMI : Muriel Dal Pont Legrand (PR), Nicolas Brisset (MCF), Nicolas Camilotto (Doctorant), Raphaël Fèvre (MCF), Alexandre Truc (post-doctorant IDEX)</p>
                    <p>- <b>Centre de Recherches en Histoires des Idées (CRHI)</b> EUR CRÉATES : Mélanie Plouviez (MCF), Stefania Ferrando (post-doc ANR PHILHERIT)</p>
                    <p>- <b>Culture, Environnement, Préhistoire, Antiquité, Moyen-âge</b> CNRS et EUR ODYSSÉE & CRÉATES : Arnaud Zucker (PR), Marco Corneli (CPJ)</p>
                    <p>- <b>Laboratoire d'Informatique, Signaux et Systèmes de Sophia Antipolis (I3S)</b> CNRS et EUR DS4H : Catherine Faron (PR), Aline Menin (MCF), Franck Michel (IR), Andrea Tettamanzi (PR), Marco Winckler (PR)</p>
                </div>
            </div>
            <p>Source: <a target="_blank" rel="noreferrer" href="https://univ-cotedazur.fr/recherche-innovation/structures-de-recherche/academies-dexcellence/academie-dexcellence-homme-idees-et-milieux/projets-de-recherche/projets-2020-2024/hisinum">UCA - Hisinum project</a></p>
        </section>
    </section>
}

export default Home;