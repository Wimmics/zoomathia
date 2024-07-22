import styles from './Footer.module.css'

import inria from '../css_modules/logo/inria.png'
import i3s from '../css_modules/logo/i3S_Couleur.png'
import cepam from '../css_modules/logo/cropped-logo_cepam.png'
import uca from '../css_modules/logo/ucajedi.png'
import cnrs from '../css_modules/logo/cnrs.png'
const Footer = () => {
    return <div className={styles["footer"]}>
        <a href='https://www.inria.fr/fr' target="_blank" rel="noreferrer"><img className={styles["img-styles"]} src={inria} alt="inria logo" /></a>
        <a href="https://www.i3s.unice.fr/fr/" target="_blank" rel="noreferrer"><img className={styles["img-styles"]} src={i3s}  alt="i3s logo"/></a>
        <a href="https://www.cepam.cnrs.fr/" target="_blank" rel="noreferrer"><img className={styles["img-styles"]} src={cepam} alt="cepam logo"/></a>
        <a href="https://univ-cotedazur.fr/universite/idex-duniversite-cote-dazur" rel="noreferrer"><img className={styles["img-styles"]} src={uca} alt="uca logo"/></a>
        <a href="https://www.cnrs.fr/fr" target="_blank" rel="noreferrer"><img className={styles["img-styles"]} src={cnrs} alt="cnrs logo"/></a>
    </div>
}
export default Footer;