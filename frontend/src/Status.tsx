import { useContext } from "react"
import { InfoContext, statusMap } from "./info"

export const Status = () => {
    const { status } = useContext(InfoContext);
    return <p>{statusMap[status]}</p>
}