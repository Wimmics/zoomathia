import styles from './Navbar.module.css'
import { Outlet, NavLink } from 'react-router-dom'

const Navbar = () => {
    return <>
        <nav id={"navbar"} className={styles['navbar']}>
            <div className={styles["logo-box"]}>

            </div>
            <div className={styles["menu-box"]}>
                <NavLink to='/' className={({ isActive }) => isActive ? 'active' : ''}>Home</NavLink>
                <NavLink to='/ExploreTheCorpus' className={({ isActive }) => isActive ? 'active' : ''}>Explore the corpus</NavLink>
                <NavLink to='/ExploreAWork' className={({ isActive }) => isActive ? 'active' : ''}>Explore a work</NavLink>
                <NavLink to='/CompetencyQuestion' className={({ isActive }) => isActive ? 'active' : ''}>Competency questions</NavLink>
            </div>
        </nav>

        <Outlet />
    </>

}

export default Navbar;