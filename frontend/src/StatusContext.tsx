import { createContext, useEffect, useState } from "react"
import { apiAddr, apiBase } from "./main";
import useWebSocket from "react-use-websocket";

export interface Status {
    isTeacher: boolean,
    pcNumber: string | null,
    name: string | null
}

interface StatusContextType {
    status: Status | null,
    setStatus: (status: Status) => void
}

export const StatusContext = createContext<StatusContextType | undefined>(undefined);

export const StatusProvider = ({ children }: { children: React.ReactNode }) => {
    const [status, setStatus] = useState<Status | null>(null);

    // Add proper WebSocket configuration
    const { lastJsonMessage, readyState } = useWebSocket(`ws://${apiAddr}/ws`, {
        shouldReconnect: (_closeEvent) => true,
        reconnectAttempts: 10,
        reconnectInterval: 3000,
    });

    // Debug WebSocket connection
    useEffect(() => {
        console.log('WebSocket readyState:', readyState);
        console.log('Last JSON message:', lastJsonMessage);
    }, [readyState, lastJsonMessage]);

    useEffect(() => {
        if (lastJsonMessage !== null) {
            console.log('Received WebSocket message:', lastJsonMessage);
            if (lastJsonMessage.type === "remove") {
                setStatus(null);
            }
        }
    }, [lastJsonMessage]);

    useEffect(() => {
        fetch(`${apiBase}/status`)
            .then(data => data.json())
            .then(setStatus)
    }, []);

    return <StatusContext.Provider value={{ status, setStatus }}>{children}</StatusContext.Provider>
}