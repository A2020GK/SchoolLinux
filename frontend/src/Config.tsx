import { useContext, useEffect, useState, useCallback } from "react"
import { StatusContext } from "./StatusContext"
import { apiService } from "./api";
import { useWebSocketConnection } from "./useWebSocketConnection";
import { PCData, WebSocketMessage } from "./types";

export const Config = () => {
    const { status } = useContext(StatusContext)!;
    if (!status?.isTeacher) return <p>У Вас нет прав на сие действо...</p>
    const [pcs, setPcs] = useState<PCData | null>(null);

    // Handle WebSocket messages for real-time updates
    const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
        switch (message.type) {
            case "pc_added":
                // Add new PC to the list
                setPcs(prev => ({
                    ...prev,
                    [message.ip]: [message.pcNumber, message.name]
                }));
                break;

            case "pc_removed":
                // Remove PC from the list
                setPcs(prev => {
                    const newPcs = { ...prev };
                    delete newPcs[message.ip];
                    return newPcs;
                });
                break;

            default:
                break;
        }
    }, []);

    useWebSocketConnection({
        onMessage: handleWebSocketMessage,
    });

    // Load initial PC list
    useEffect(() => {
        apiService.getPCs()
            .then(setPcs)
            .catch(console.error);
    }, []);

    const delpc = (ip: string) => {
        apiService.deletePC(ip)
            .then(data => {
                if (data.ok && data.data) {
                    setPcs(data.data);
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