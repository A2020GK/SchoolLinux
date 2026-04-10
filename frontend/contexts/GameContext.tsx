import React, { createContext, useContext, useEffect, useState } from "react";
import type { GameResponseSafe } from "../types/game";
import { getCurrentGame } from "../api/game";
import { onSocketEvent } from "../api/socket";

export interface GameContextValue {
    game: GameResponseSafe | null;
    loading: boolean;
    error: Error | null;
    refetch: () => Promise<void>;
}

const GameContext = createContext<GameContextValue | undefined>(undefined);

export const GameProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [game, setGame] = useState<GameResponseSafe | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchGame = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await getCurrentGame();
            setGame(response);
        } catch (err) {
            setError(err instanceof Error ? err : new Error(String(err)));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGame();

        // Subscribe to game_change socket events
        const unsubscribe = onSocketEvent("game_change", (gamePayload) => {
            setGame(gamePayload as GameResponseSafe);
        });

        return () => unsubscribe();
    }, []);

    const value: GameContextValue = {
        game,
        loading,
        error,
        refetch: fetchGame,
    };

    return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
};

export const useGame = (): GameContextValue => {
    const context = useContext(GameContext);
    if (!context) {
        throw new Error("useGame must be used within GameProvider");
    }
    return context;
};
