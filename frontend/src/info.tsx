import { createContext, useEffect, useState, type Dispatch, type ReactNode, type SetStateAction } from "react";
import { api, socket } from "./api";

export type Status = "reg" | "init" | "run";


export interface Info {
    isTeacher: boolean,
    status: Status,
    loaded:boolean
}


export const InfoContext = createContext<Info & { setInfo: Dispatch<SetStateAction<Info>> }>(
    { isTeacher: false, status: "reg", setInfo: () => { }, loaded:false }
);

export const InfoProvider = ({ children }: { children: ReactNode }) => {
    const [info, setInfo] = useState<Info>({ isTeacher: false, status: "reg", loaded:true });
    useEffect(() => { (async () => setInfo((await api.get("/info")).data))(); setInfo({...info, loaded:true}) }, [setInfo])
    useEffect(() => {
        const onInfoUpdate = (infoNew: Info) => setInfo({ ...info, ...infoNew });
        socket.on("info", onInfoUpdate)
        return () => {
            socket.off("info", onInfoUpdate)
        }
    }, [info])

    return <InfoContext.Provider value={{ ...info, setInfo: setInfo }}>{children}</InfoContext.Provider>
}