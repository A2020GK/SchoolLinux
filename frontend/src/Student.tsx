import { useContext, useEffect, useState } from "react"
import { InfoContext } from "./info"
import { StudentLoginForm } from "./StudentLoginForm";
import { api, socket } from "./api";
import { StudentInfo } from "./StudentInfo";

export interface Me {
    pc: string,
    name: string,
    klads: number
}

export const Student = () => {
    const { status } = useContext(InfoContext);

    const [me, setMe] = useState<Me | null | "checking">(null);
    useEffect(() => { (async () => setMe((await api.get("/students/me")).data))() }, [setMe]);
    useEffect(() => {
        const kick = () => setMe(null);
        socket.on("kick", kick);
        return () => {
            socket.off("kick", kick)
        }
    }, [me])

    const login = (pc: string, name: string) => {
        setMe("checking");
        api.post("/students/reg", { pc, name }).then(t => {
            const data = t.data;
            if (!data) {
                alert("Ваш компьютер не прошёл проверку на совместимость с системой. Обратитесь к учителю.");
                setMe(null);
            }
            else setMe(data);
        });
    }


    return <>
        {(status == "reg" && (me == null || me == "checking")) ? <StudentLoginForm handler={login} me={me} /> : <StudentInfo meState={{ me, setMe } as any} />}
    </>
}