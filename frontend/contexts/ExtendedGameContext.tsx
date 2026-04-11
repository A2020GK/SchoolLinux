import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { GameChangeRequest, GameResponse } from "../types/game";
import { listGames, getCurrentGame, setCurrentGame as setCurrentGameAPI } from "../api/game";
import { toError } from "../helpers/error";
import { frontendEnv } from "../config/env";
import { useUser } from "./UserContext";

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
    const { user } = useUser();
    const [currentGame, setCurrentGameState] = useState<GameResponse | null>(null);
    const [gamesList, setGamesList] = useState<Record<string, GameResponse> | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchCurrentGame = useCallback(async () => {
        if (frontendEnv.mockPreview.enabled) {
            setLoading(false);
            setError(null);
            setCurrentGameState(frontendEnv.mockPreview.currentGame);
            return;
        }

        try {
            setLoading(true);
            setError(null);
            const response = await getCurrentGame();
            setCurrentGameState(response as GameResponse | null);
        } catch (err) {
            setError(toError(err));
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchGamesList = useCallback(async () => {
        if (frontendEnv.mockPreview.enabled) {
            setError(null);
            setGamesList(frontendEnv.mockPreview.gamesList);
            return;
        }

        if (!user?.isTeacher) {
            setGamesList(null);
            setError(null);
            return;
        }

        try {
            setError(null);
            const response = await listGames();
            setGamesList(response);
        } catch (err) {
            setError(toError(err));
        }
    }, [user?.isTeacher]);

    const handleSetCurrentGame = useCallback(async (gameKey: string, settings?: Record<string, string | number | boolean>) => {
        if (frontendEnv.mockPreview.enabled) {
            const selectedGame = (gamesList ?? frontendEnv.mockPreview.gamesList)[gameKey];
            if (!selectedGame) {
                throw new Error("Unknown mock game key");
            }

            setCurrentGameState({
                ...selectedGame,
                settings: {
                    ...selectedGame.settings,
                    ...(settings ?? {}),
                },
            });
            return;
        }

        try {
            setError(null);
            const payload: GameChangeRequest = { gameKey, settings };
            const response = await setCurrentGameAPI(payload);
            setCurrentGameState(response);
        } catch (err) {
            setError(toError(err));
            throw err;
        }
    }, []);

    useEffect(() => {
        fetchCurrentGame();
        if (user?.isTeacher || frontendEnv.mockPreview.enabled) {
            fetchGamesList();
        } else {
            setGamesList(null);
        }
    }, [fetchCurrentGame, fetchGamesList, user?.isTeacher]);

    const value: ExtendedGameContextValue = useMemo(() => ({
        currentGame,
        gamesList,
        loading,
        error,
        setCurrentGame: handleSetCurrentGame,
        refetchCurrent: fetchCurrentGame,
        refetchList: fetchGamesList,
    }), [currentGame, error, fetchCurrentGame, fetchGamesList, gamesList, handleSetCurrentGame, loading]);

    return <ExtendedGameContext.Provider value={value}>{children}</ExtendedGameContext.Provider>;
};

export const useExtendedGame = (): ExtendedGameContextValue => {
    const context = useContext(ExtendedGameContext);
    if (!context) {
        throw new Error("useExtendedGame must be used within ExtendedGameProvider");
    }
    return context;
};
