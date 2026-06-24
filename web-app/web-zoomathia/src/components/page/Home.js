import styles from "./Home.module.css"
import { NavLink } from 'react-router-dom'

const Home = () => {
    return <section className={styles["box-content"]}>
        <section className={styles["hero"]}>
            <h1 className={styles["hero-title"]}>Explore Zoological Knowledge</h1>
            <p className={styles["hero-subtitle"]}>
                Study the transmission of zoological knowledge from Antiquity to the Middle Ages
            </p>
            <div className={styles["hero-buttons"]}>
                <NavLink to='/ExploreTheCorpus' className={styles["btn-primary"]}>Explore the corpus</NavLink>
                <NavLink to='/ExploreAWork' className={styles["btn-primary"]}>Explore a work</NavLink>
                <NavLink to='/CompetencyQuestion' className={styles["btn-primary"]}>Competency questions</NavLink>
            </div>
        </section>
    </section>
}

export default Home;