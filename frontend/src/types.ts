// WebSocket message types
export interface BaseWebSocketMessage {
    type: string;
}

export interface PingMessage extends BaseWebSocketMessage {
    type: "ping";
    message: string;
}

export interface RemoveMessage extends BaseWebSocketMessage {
    type: "remove";
}

export interface PCAddedMessage extends BaseWebSocketMessage {
    type: "pc_added";
    ip: string;
    pcNumber: string;
    name: string;
}

export interface PCRemovedMessage extends BaseWebSocketMessage {
    type: "pc_removed";
    ip: string;
}

export type WebSocketMessage = 
    | PingMessage 
    | RemoveMessage 
    | PCAddedMessage 
    | PCRemovedMessage;

// API types
export interface Status {
    configured: boolean;
    isTeacher: boolean;
    pcNumber: string | null;
    name: string | null;
}

export interface PCData {
    [ip: string]: [string, string]; // [pcNumber, name]
}

export interface RegPCRequest {
    pcNumber: string;
    name: string;
}

export interface APIResponse<T = any> {
    ok: boolean;
    error?: string;
    data?: T;
}
