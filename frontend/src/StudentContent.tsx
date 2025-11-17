import { useContext, useState, type Dispatch, type SetStateAction } from "react";
import type { Me } from "./Student";
import { Status } from "./Status";
import { api } from "./api";
import { InfoContext } from "./info";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowUpFromBracket, faComputer, faGem, faRightFromBracket, faUser } from "@fortawesome/free-solid-svg-icons";

export const StudentContent = ({ meState }: { meState: { me: Me | null, setMe: Dispatch<SetStateAction<Me | null>> } }) => {
    const { status } = useContext(InfoContext);

    const [klad, setKlad] = useState("")


    const logout = async () => {
        const t = (await api.post("/students/logout")).data;
        if (!t) alert("Не получилось выйти :(");
        else meState.setMe(null);
    }

    const tryKlad = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const r = (await api.post(`/game/klad`, { value: klad })).data;
        (e.target as any).reset();
        if (r) {
            meState.setMe(r);
            alert(`Ура, верно! Вы нашли клад ${r.klads}/5, так держать`);
        } else {
            alert("Упс, что-то да не так... Такого клада нет или вы отправляли его ранее.");
        }
    }

    return <>
        <h1><FontAwesomeIcon icon={faComputer} /> {meState.me?.pc}</h1>
        <h2><FontAwesomeIcon icon={faUser} /> {meState.me?.name}</h2>
        <Status />
        {status == "run" && ((meState.me?.klads ?? 0) < 5 ? (<form onSubmit={tryKlad}>
            <hr /><p><label htmlFor="klad"><FontAwesomeIcon icon={faGem} /> Клад: </label><input onChange={e => setKlad(e.target.value)} id="klad" /><button type="submit"><FontAwesomeIcon icon={faArrowUpFromBracket} /> Отправить</button></p><hr />
        </form>) : (<p>Вы нашли все клады :)</p>))}

        <p><button onClick={logout}><FontAwesomeIcon icon={faRightFromBracket} /> Выйти</button></p>
    </>
}