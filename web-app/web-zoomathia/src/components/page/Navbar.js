import styles from './Navbar.module.css'
import { Outlet, NavLink } from 'react-router-dom'

const Navbar = () => {
    return <>
        <nav className={styles['navbar']}>
            <div className={styles["logo-box"]}>

            </div>
            <div className={styles["menu-box"]}>
                <NavLink to='/' activeClassName='active'>Home</NavLink>
                <NavLink to='/ExploreTheCorpus' activeClassName='active'>Explore the corpus</NavLink>
                <NavLink to='/ExploreAWork' activeClassName='active'>Explore a work</NavLink>
                <NavLink to='/CompetencyQuestion' activeClassName='active'>Competency question</NavLink>
            </div>
        </nav>

        <Outlet />
    </>

}

export default Navbar;