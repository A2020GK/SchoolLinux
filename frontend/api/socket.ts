import type { Socket } from "socket.io-client";

import { socket } from "./api";
import type { ClientToServerEvents, ServerToClientEvents, SocketEventName } from "../types/socket";

export const typedSocket = socket as Socket<ServerToClientEvents, ClientToServerEvents>;

export function connectSocket(): void {
    typedSocket.connect();
}

export function disconnectSocket(): void {
    typedSocket.disconnect();
}

export function onSocketEvent<EventName extends SocketEventName>(
    eventName: EventName,
    handler: ServerToClientEvents[EventName],
): () => void {
    typedSocket.on(eventName, handler as any);
    return () => typedSocket.off(eventName, handler as any);
}

export function offSocketEvent<EventName extends SocketEventName>(
    eventName: EventName,
    handler: ServerToClientEvents[EventName],
): void {
    typedSocket.off(eventName, handler as any);
}