import { useContext, useEffect, useState } from "react"
import { StatusContext } from "./StatusContext"
import { apiBase } from "./main";
import useWebSocket from "react-use-websocket";

interface PCData {
    [ip: string]: [string, string]; // [pcNumber, name]
}

export const Config = () => {
    const { status } = useContext(StatusContext)!;
    if (!status?.isTeacher) return <p>У Вас нет прав на сие действо...</p>
    const [pcs, setPcs] = useState<PCData | null>(null);

    const { lastJsonMessage } = useWebSocket(`ws://${window.location.hostname}:8000/ws`, {
        shouldReconnect: () => true,
    });

    // Load initial PC list
    useEffect(() => {
        fetch(`${apiBase}/pcs`)
            .then(data => data.json())
            .then(setPcs)
            .catch(console.error);
    }, []);

    // Handle WebSocket messages for real-time updates
    useEffect(() => {
        if (lastJsonMessage) {
            console.log('WebSocket message:', lastJsonMessage);

            switch (lastJsonMessage.type) {
                case "pc_added":
                    // Add new PC to the list
                    setPcs(prev => ({
                        ...prev,
                        [lastJsonMessage.ip]: [lastJsonMessage.pcNumber, lastJsonMessage.name]
                    }));
                    break;

                case "pc_removed":
                    // Remove PC from the list
                    setPcs(prev => {
                        const newPcs = { ...prev };
                        delete newPcs[lastJsonMessage.ip];
                        return newPcs;
                    });
                    break;

                default:
                    break;
            }
        }
    }, [lastJsonMessage]);

    const delpc = (ip: string) => {
        fetch(`${apiBase}/pcs/${ip}`, {
            method: "DELETE"
        })
            .then(data => data.json())
            .then(data => {
                if (data.ok) {
                    setPcs(data.pcs);
                }
            })
            .catch(console.error);
    }

    if (!status) return <p>Загрузка...</p>

    if (!pcs) return <p>Загрузка...</p>

    return (
        <div>
            <h2>Управление компьютерами</h2>
            <table width="100%" border={1}>
                <thead>
                    <tr>
                        <th>IP</th>
                        <th>Номер</th>
                        <th>Человек</th>
                        <th>Действо</th>
                    </tr>
                </thead>
                <tbody>
                    {Object.keys(pcs).map(ip => (
                        <tr key={ip}>
                            <td>{ip}</td>
                            <td>{pcs[ip][0]}</td>
                            <td>{pcs[ip][1]}</td>
                            <td>
                                <button onClick={() => delpc(ip)}>
                                    Убрать
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {Object.keys(pcs).length === 0 && (
                <p>Нет зарегистрированных компьютеров</p>
            )}
        </div>
    );
}