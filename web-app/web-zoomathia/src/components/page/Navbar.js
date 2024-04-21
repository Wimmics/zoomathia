import styles from './Navbar.module.css'
import { Outlet, Link } from 'react-router-dom'

const Navbar = () => {
    return <>
        <nav className={styles['navbar']}>
            <div className={styles["logo-box"]}>

            </div>
            <div className={styles["menu-box"]}>
                <Link to='/' >Home</Link>
                <Link to='/ExploreTheCorpus'>Explore the corpus</Link>
                <Link to='/ExploreAWork'>Explore a work</Link>
                <Link to='/CompetencyQuestion'>Competency question</Link>
            </div>
        </nav>

        <Outlet />
    </>

}

export default Navbar;