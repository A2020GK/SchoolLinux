import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { GameResponseSafe } from "../types/game";
import { getCurrentGame } from "../api/game";
import { onSocketEvent } from "../api/socket";
import { toError } from "../helpers/error";
import { frontendEnv } from "../config/env";

export type GameState = "idle" | "init" | "running" | "stopped";

export interface GameContextValue {
    game: GameResponseSafe | null;
    gameState: GameState;
    loading: boolean;
    error: Error | null;
    refetch: () => Promise<void>;
}

const GameContext = createContext<GameContextValue | undefined>(undefined);

export const GameProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [game, setGame] = useState<GameResponseSafe | null>(null);
    const [gameState, setGameState] = useState<GameState>("idle");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchGame = useCallback(async () => {
        if (frontendEnv.mockPreview.enabled) {
            setLoading(false);
            setError(null);
            setGame(frontendEnv.mockPreview.currentGame);
            setGameState(frontendEnv.mockPreview.gameState);
            return;
        }

        try {
            setLoading(true);
            setError(null);
            const response = await getCurrentGame();
            setGame(response);
        } catch (err) {
            setError(toError(err));
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchGame();

        if (frontendEnv.mockPreview.enabled) {
            return;
        }

        // Subscribe to game_change socket events
        const unsubscribe1 = onSocketEvent("game_change", (gamePayload) => {
            setGame(gamePayload as GameResponseSafe);
        });

        // Subscribe to game_state_changed socket events
        const unsubscribe2 = onSocketEvent("game_state_changed", (payload) => {
            setGameState(payload.state as GameState);
        });

        return () => {
            unsubscribe1();
            unsubscribe2();
        };
    }, []);

    const value: GameContextValue = useMemo(() => ({
        game,
        gameState,
        loading,
        error,
        refetch: fetchGame,
    }), [error, fetchGame, game, gameState, loading]);

    return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
};

export const useGame = (): GameContextValue => {
    const context = useContext(GameContext);
    if (!context) {
        throw new Error("useGame must be used within GameProvider");
    }
    return context;
};
