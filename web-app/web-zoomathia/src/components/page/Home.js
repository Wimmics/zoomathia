import styles from "./Home.module.css"
const Home = () => {
    return <section className={styles["box-content"]}>
        <h1>Welcome to Zoomathia</h1>
        <section className={styles["home-project"]}>
            <h2>About Zoomathia</h2>
            <p>
                The project ZOOMATHIA aims to study the formation and transmission of ancient zoological knowledge over a long period, with an historical, literary and epistemological approach, through texts and iconography, especially in a pivotal period (late Antiquity and the Early Middle Ages), presenting a large dispersion and a wide range of atypical relay of this knowledge. This project is inspired by the the program « Seminars of history on zoological knowledge » led by Liliane Bodson in Liege from 1989 to 2004. This project is motivated by the lack of research coordination on the area, and aims to establish a synergy of investigations often solitary or focused on very limitated corpus or topics. Generally limitated to a few central figures and lamenting the « disappearance of Aristotle’s biology » (J.G. Lennox), the research on ancient zoology needs a more extensive, synthetic and diachronic approach. The purpose is to build a critical and methodological history of zoological knowledge, enlightening overlooked periods or process of the transmission and social/literary mutation of this knowledge. This diachronic synthesis has to take into account the different dimensions of zoological knowledge (through texts, images and biological data): biology, epistemology, history, philology, archeology, philosophy and technology.
            </p>
            <h2>About Hisinum project</h2>
            <h4>Context</h4>
            <p>La transformation numérique affecte profondément les pratiques des chercheurs dans le domaine des sciences humaines et sociales (SHS) jusqu’à questionner les frontières des disciplines. Par ailleurs, les outils numériques partagés agissent comme un catalyseur méthodologique entre disciplines suggérant une interdisciplinarité renouvelée, que ce soit au sein même des SHS ou entre les SHS et les sciences dites "dures".</p>
            <p>La question de la donnée en sciences humaines et sociales revêt des réalités multiples, et les nouvelles pratiques offertes par les outils numériques également. Ces pratiques requièrent l’acquisition de nouvelles compétences mais elles s’articulent sur l’usage d’outils partagés ou similaires, de bases de données communes, de méthodologies réplicables.</p>
            <h4>Objectifs</h4>
            <p>Ce projet pluridisciplinaire et fédérateur réunit trois équipes, quatre laboratoires et des partenaires extérieurs dans une démarche structurante et ouverte afin de mutualiser des outils liés, interopérables et généralisables.</p>
            <p>Il s'agit de mettre en commun compétences, outils et réflexions méthodologiques lors d’une première étape exploratoire, et exploiter les synergies entre les programmes pour une montée en compétence, une diffusion et une cristallisation de ces savoirs, pour engager une dynamique de site durable par des séminaires de mise en commun des problématiques et des résultats, et par de la formation.</p>
            <p>L’objectif à moyen terme est de candidater à des appels qui financent l’acquisition d’infrastructures numériques ou des projets de recherche communs transdisciplinaires.</p>
        </section>
    </section>
}

export default Home;