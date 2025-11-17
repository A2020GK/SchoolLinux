import { useContext } from "react"
import { InfoContext } from "./info"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGear, faHourglassHalf, faPlay } from "@fortawesome/free-solid-svg-icons";

export const statusMap = {
    reg: <><FontAwesomeIcon icon={faHourglassHalf} /> Ожидание регистрации всех комьютеров...</>,
    init: <><FontAwesomeIcon icon={faGear} className="spinner" /> Инициализация игры...</>,
    run: <><FontAwesomeIcon icon={faPlay} /> Игра идёт</>
}

export const Status = () => {
    const { status } = useContext(InfoContext);
    return <p>{statusMap[status]}</p>
}