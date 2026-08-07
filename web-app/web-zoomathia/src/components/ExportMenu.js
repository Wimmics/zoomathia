import { useState, useRef, useEffect } from "react"
import styles from "./css_modules/ExportMenu.module.css"

/**
 * Reusable compact export menu: a single discreet button that reveals a
 * list of export format options on click, instead of one visible
 * button/link per format. Adding or removing a format only means changing
 * the `options` array passed in, not the component itself.
 */
const ExportMenu = ({ label = "Export", options = [] }) => {
    const [open, setOpen] = useState(false)
    const containerRef = useRef(null)

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (containerRef.current && !containerRef.current.contains(e.target)) {
                setOpen(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside)
        return () => document.removeEventListener("mousedown", handleClickOutside)
    }, [])

    if (!options.length) return null

    return <div className={styles["export-menu"]} ref={containerRef}>
        <button
            type="button"
            className={styles["export-toggle"]}
            onClick={() => setOpen((v) => !v)}
            aria-haspopup="true"
            aria-expanded={open}>
            {label} <span className={styles["arrow"]}>{open ? "▲" : "▼"}</span>
        </button>
        {open && (
            <ul className={styles["export-list"]}>
                {options.map((opt) => (
                    <li key={opt.label}>
                        <a
                            href={opt.href}
                            download={opt.download === undefined ? true : opt.download}
                            target="_blank"
                            rel="noreferrer"
                            onClick={() => setOpen(false)}>
                            {opt.label}
                        </a>
                    </li>
                ))}
            </ul>
        )}
    </div>
}

export default ExportMenu
