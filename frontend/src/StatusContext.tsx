import { createContext, useEffect, useState } from "react"
import { apiBase } from "./main";
import { useWebSocketConnection } from "./useWebSocketConnection";
import { Status, WebSocketMessage } from "./types";

// Status interface is now imported from types.ts

interface StatusContextType {
    status: Status | null,
    setStatus: (status: Status) => void,
    isWebSocketConnected: boolean
}

export const StatusContext = createContext<StatusContextType | undefined>(undefined);

export const StatusProvider = ({ children }: { children: React.ReactNode }) => {
    const [status, setStatus] = useState<Status | null>(null);

    // Handle WebSocket messages
    const handleWebSocketMessage = (message: WebSocketMessage) => {
        if (message.type === "remove") {
            setStatus(null);
        }
    };

    const { isConnected } = useWebSocketConnection({
        onMessage: handleWebSocketMessage,
    });

    // Load initial status
    useEffect(() => {
        fetch(`${apiBase}/status`)
            .then(data => data.json())
            .then(setStatus)
            .catch(console.error);
    }, []);

    return <StatusContext.Provider value={{ status, setStatus, isWebSocketConnected: isConnected }}>{children}</StatusContext.Provider>
}