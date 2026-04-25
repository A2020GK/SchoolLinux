import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faLinux } from '@fortawesome/free-brands-svg-icons'

export const Header = () => {
    return (
        <header>
            <a href="#top" style={{ textDecoration: 'none', margin: 0 }}>
                <h1>
                    <FontAwesomeIcon icon={faLinux} /> School Linux
                </h1>
            </a>
            <nav>
                <a href="#problem">Проблема и решение</a>
                <a href="#features">Возможности</a>
                <a href="#links">Ресурсы</a>
            </nav>
        </header>
    )
}
