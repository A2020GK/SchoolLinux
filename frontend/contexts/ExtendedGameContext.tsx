import React, { createContext, useContext, useEffect, useState } from "react";
import type { GameChangeRequest, GameResponse } from "../types/game";
import { listGames, getCurrentGame, setCurrentGame as setCurrentGameAPI } from "../api/game";

export interface ExtendedGameContextValue {
    currentGame: GameResponse | null;
    gamesList: Record<string, GameResponse> | null;
    loading: boolean;
    error: Error | null;
    setCurrentGame: (gameKey: string, settings?: Record<string, string | number | boolean>) => Promise<void>;
    refetchCurrent: () => Promise<void>;
    refetchList: () => Promise<void>;
}

const ExtendedGameContext = createContext<ExtendedGameContextValue | undefined>(undefined);

export const ExtendedGameProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [currentGame, setCurrentGameState] = useState<GameResponse | null>(null);
    const [gamesList, setGamesList] = useState<Record<string, GameResponse> | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchCurrentGame = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await getCurrentGame();
            setCurrentGameState(response as GameResponse | null);
        } catch (err) {
            setError(err instanceof Error ? err : new Error(String(err)));
        } finally {
            setLoading(false);
        }
    };

    const fetchGamesList = async () => {
        try {
            setError(null);
            const response = await listGames();
            setGamesList(response);
        } catch (err) {
            setError(err instanceof Error ? err : new Error(String(err)));
        }
    };

    const handleSetCurrentGame = async (gameKey: string, settings?: Record<string, string | number | boolean>) => {
        try {
            setError(null);
            const payload: GameChangeRequest = { gameKey, settings };
            const response = await setCurrentGameAPI(payload);
            setCurrentGameState(response);
        } catch (err) {
            setError(err instanceof Error ? err : new Error(String(err)));
            throw err;
        }
    };

    useEffect(() => {
        fetchCurrentGame();
        fetchGamesList();
    }, []);

    const value: ExtendedGameContextValue = {
        currentGame,
        gamesList,
        loading,
        error,
        setCurrentGame: handleSetCurrentGame,
        refetchCurrent: fetchCurrentGame,
        refetchList: fetchGamesList,
    };

    return <ExtendedGameContext.Provider value={value}>{children}</ExtendedGameContext.Provider>;
};

export const useExtendedGame = (): ExtendedGameContextValue => {
    const context = useContext(ExtendedGameContext);
    if (!context) {
        throw new Error("useExtendedGame must be used within ExtendedGameProvider");
    }
    return context;
};
