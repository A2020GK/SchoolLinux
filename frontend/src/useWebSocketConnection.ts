import { useEffect, useCallback, useRef } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { WebSocketMessage } from './types';
import { apiAddr } from './api';

interface UseWebSocketConnectionOptions {
    onMessage?: (message: WebSocketMessage) => void;
    onConnect?: () => void;
    onDisconnect?: () => void;
    shouldReconnect?: (closeEvent: CloseEvent) => boolean;
    reconnectAttempts?: number;
    reconnectInterval?: number;
    enableHeartbeat?: boolean;
    heartbeatInterval?: number;
}

export const useWebSocketConnection = (options: UseWebSocketConnectionOptions = {}) => {
    const {
        onMessage,
        onConnect,
        onDisconnect,
        shouldReconnect = (closeEvent) => {
            // Don't reconnect on normal closure or if we've exceeded max attempts
            return closeEvent.code !== 1000;
        },
        reconnectAttempts = 10,
        reconnectInterval = 3000,
        enableHeartbeat = true,
        heartbeatInterval = 30000, // 30 seconds
    } = options;

    const heartbeatRef = useRef<number | null>(null);

    const { lastJsonMessage, readyState, sendMessage, getWebSocket } = useWebSocket(
        `ws://${apiAddr}/ws`,
        {
            shouldReconnect,
            reconnectAttempts,
            reconnectInterval,
            onOpen: () => {
                onConnect?.();
                // Start heartbeat if enabled
                if (enableHeartbeat) {
                    startHeartbeat();
                }
            },
            onClose: () => {
                onDisconnect?.();
                stopHeartbeat();
            },
            onError: (error) => {
                console.error('WebSocket error:', error);
            },
        }
    );

    // Handle incoming messages
    useEffect(() => {
        if (lastJsonMessage && onMessage) {
            onMessage(lastJsonMessage as WebSocketMessage);
        }
    }, [lastJsonMessage, onMessage]);

    // Send ping to keep connection alive
    const sendPing = useCallback(() => {
        if (readyState === ReadyState.OPEN) {
            sendMessage("ping");
        }
    }, [readyState, sendMessage]);

    // Heartbeat functionality
    const startHeartbeat = useCallback(() => {
        stopHeartbeat(); // Clear any existing heartbeat
        heartbeatRef.current = setInterval(() => {
            sendPing();
        }, heartbeatInterval);
    }, [sendPing, heartbeatInterval]);

    const stopHeartbeat = useCallback(() => {
        if (heartbeatRef.current) {
            clearInterval(heartbeatRef.current);
            heartbeatRef.current = null;
        }
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopHeartbeat();
        };
    }, [stopHeartbeat]);

    return {
        lastJsonMessage: lastJsonMessage as WebSocketMessage | null,
        readyState,
        sendMessage,
        sendPing,
        isConnected: readyState === ReadyState.OPEN,
        isConnecting: readyState === ReadyState.CONNECTING,
        isDisconnected: readyState === ReadyState.CLOSED || readyState === ReadyState.CLOSING,
        getWebSocket,
    };
};
