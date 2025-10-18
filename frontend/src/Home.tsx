import { useContext, useState, type FormEventHandler } from "react";
import { StatusContext, type Status } from "./StatusContext";
import { Link } from "react-router";
import { apiBase } from "./main";

export const Home = () => {
    const { status, setStatus } = useContext(StatusContext)!;
    const [pc, setPc] = useState("");
    const [name, setName] = useState("");


    const registerPc: FormEventHandler<HTMLFormElement> = e => {
        e.preventDefault();
        fetch(`${apiBase}/pcs/reg`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pcNumber: pc, name: name })
        })
            .then(data => data.json())
            .then(data => {
                if (!data.ok) return alert("Что-то не так...")
                setStatus({ ...status, pcNumber: data.pcNumber, name:name } as Status)
            });
    }

    if (status?.isTeacher) return <p><Link to="/config" className="button">Компьютеры</Link></p>


    if (!status?.pcNumber) return <form onSubmit={registerPc}>
        <p><label htmlFor="pc-number">Номер компьютера (&lt;кабинет&gt;-&lt;компьютер&gt;)</label></p>
        <p><input id="pc-number" placeholder="<кабинет>-<компьютер>" onChange={e => setPc(e.target.value)} /></p>
        <p><label htmlFor="name">ФИО</label></p>
        <p><input id="name" placeholder="Тест Тестовский" onChange={e => setName(e.target.value)} /></p>
        <p><button type="submit" disabled={!(pc && pc.match(/^\d+-\d+$/))}>Войти</button></p>

    </form>

    return <>
        <p><b>Номер компьютера: </b>{status.pcNumber}</p>
        <p><b>Имя:</b>{status.name}</p>
        <p><i>(Обратитесь к учителю, если эта информация неверна)</i></p>
    </>
}