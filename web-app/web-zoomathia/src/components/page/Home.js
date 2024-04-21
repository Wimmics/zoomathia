import styles from "./Home.module.css"
const Home = () => {
    return <section className={styles["box-content"]}>
        <h1>Welcome to Zoomathia</h1>
        <section className={styles["home-project"]}>
            <h2>Overall presentation of the project</h2>
            <p>
                The project ZOOMATHIA aims to study the formation and transmission of ancient zoological knowledge over a long period, with an historical, literary and epistemological approach, through texts and iconography, especially in a pivotal period (late Antiquity and the Early Middle Ages), presenting a large dispersion and a wide range of atypical relay of this knowledge. This project is inspired by the the program « Seminars of history on zoological knowledge » led by Liliane Bodson in Liege from 1989 to 2004. This project is motivated by the lack of research coordination on the area, and aims to establish a synergy of investigations often solitary or focused on very limitated corpus or topics. Generally limitated to a few central figures and lamenting the « disappearance of Aristotle’s biology » (J.G. Lennox), the research on ancient zoology needs a more extensive, synthetic and diachronic approach. The purpose is to build a critical and methodological history of zoological knowledge, enlightening overlooked periods or process of the transmission and social/literary mutation of this knowledge. This diachronic synthesis has to take into account the different dimensions of zoological knowledge (through texts, images and biological data): biology, epistemology, history, philology, archeology, philosophy and technology.
            </p>
        </section>
    </section>
}

export default Home;