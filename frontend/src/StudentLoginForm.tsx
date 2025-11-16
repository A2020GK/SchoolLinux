import { useState } from "react";
import type { Me } from "./Student";

export const StudentLoginForm = ({ handler, me }: { handler: (pc: string, name: string) => void, me: Me | null | "checking" }) => {

    const [pc, setPc] = useState("");
    const [name, setName] = useState("");

    return <>
        <h1>Регистрация</h1>
        <form onSubmit={event => {
            event.preventDefault();
            handler(pc, name);
        }}>
            <p><label htmlFor="pc">Номер компьютера</label></p>
            <details>
                <summary>Рекомендуемый формат</summary>
                <p><i style={{ color: "darkgray" }}>Формат: &lt;номер кабинета&gt;-&lt;номер компьютера&gt;, пример: 403-1</i></p>
            </details>
            <p><input id="pc" onChange={e => setPc(e.target.value)} placeholder="Номер компьютера"></input></p>

            <hr />

            <p><label htmlFor="name">Полное имя</label></p>
            <details>
                <summary>Рекомендуемый формат</summary>
                <p><i style={{ color: "darkgray" }}>Формат: &lt;Имя&gt; &lt;Фамилия&gt;, пример: Тест Тестовский</i></p>
                <p><i style={{ color: "darkgray" }}>При работе в команде из нескольких человек указывайте имена и фамилии через запятую</i></p>
            </details>
            <p><input id="name" onChange={e => setName(e.target.value)} placeholder="Полное имя"></input></p>

            <p><button type="submit">Подключиться</button></p>
            {me == "checking" && <p className="checking"><b>Ваш компьютер проверяется, пожалуйста подождите...</b></p>}
            <p><i style={{ color: "darkgray" }}><small>Вы можете быть дискфалифицированны за грубое несоответствие данных формату/некорректные данные</small></i></p>
        </form>
    </>
}