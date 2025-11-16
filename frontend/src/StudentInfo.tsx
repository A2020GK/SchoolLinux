import { type Dispatch, type SetStateAction } from "react";
import type { Me } from "./Student";
import { Status } from "./Status";
import { api } from "./api";

export const StudentInfo = ({ meState }: { meState: { me: Me | null, setMe: Dispatch<SetStateAction<Me | null>> } }) => {

    const logout = async () => {
        const t = (await api.post("/students/logout")).data;
        if(!t) alert("Не получилось выйти :(");
        else meState.setMe(null);
    }

    return <>
        <h1>{meState.me?.pc}</h1>
        <h2>{meState.me?.name}</h2>
        <Status/>
        <p><button onClick={logout}>Выйти</button></p>
    </>
}