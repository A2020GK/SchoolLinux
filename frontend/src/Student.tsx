import { useEffect, useState } from "react"
import { StudentLoginForm } from "./StudentLoginForm";
import { api, socket } from "./api";
import { StudentContent } from "./StudentContent";

export interface Me {
    pc: string,
    name: string,
    klads: number
}

export const Student = () => {
    const [me, setMe] = useState<Me | null | "checking">(null);
    useEffect(() => { (async () => setMe((await api.get("/students/me")).data))() }, [setMe]);
    useEffect(() => {
        const update = (d: Me | null) => setMe(d);
        socket.on("update", update);
        return () => {
            socket.off("update", update)
        }
    }, [me])

    const login = (pc: string, name: string) => {
        setMe("checking");
        api.post("/students/reg", { pc, name }).then(t => {
            const data = t.data;
            if (!data) {
                alert("Ваш компьютер не прошёл проверку на совместимость с системой. Обратитесь к учителю.");
                setMe(null);
            } else if (data == 'rejected') {
                alert("Игра недоступна, Вы были изгнаны или вышли из запущенной игры. Ожидайте следующего раунда.");
                setMe(null);
            }
            else setMe(data);
        });
    }


    return <>
        {(me == null || me == "checking") ? <StudentLoginForm handler={login} me={me} /> : <StudentContent meState={{ me, setMe } as any} />}
    </>
}