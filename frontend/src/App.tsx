import { useContext } from "react"
import { Teacher } from "./Teacher";
import { Student } from "./Student";
import { InfoContext } from "./info";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGithubSquare, faLinux } from "@fortawesome/free-brands-svg-icons";
import { faCircleNotch } from "@fortawesome/free-solid-svg-icons";

export const App = () => {
    const { isTeacher, loaded } = useContext(InfoContext);

    return <>
        <header>
            <h1>
                <a href="/"><FontAwesomeIcon icon={faLinux} /> School Linux</a>
            </h1>
        </header>
        <main>
            <div className="content">
                {!loaded ? (isTeacher ? <Teacher /> : <Student />) : <p><FontAwesomeIcon icon={faCircleNotch} className="spinner" />Загрузка...</p>}
            </div>
        </main>
        <footer><a href="https://github.com/A2020GK/SchoolLinux"><FontAwesomeIcon icon={faGithubSquare} /></a></footer>

    </>
}