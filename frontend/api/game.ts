import { api } from "./api";
import type {
    GameChangeRequest,
    GameResponse,
    GameResponseSafe,
} from "../types/game";

const GAME_PREFIX = "/game";

export async function getCurrentGame(): Promise<GameResponseSafe | GameResponse | null> {
    const response = await api.get<GameResponseSafe | GameResponse | null>(`${GAME_PREFIX}/`);
    return response.data;
}

export async function listGames(): Promise<Record<string, GameResponse>> {
    const response = await api.get<Record<string, GameResponse>>(`${GAME_PREFIX}/list`);
    return response.data;
}

export async function setCurrentGame(payload: GameChangeRequest): Promise<GameResponse> {
    const response = await api.post<GameResponse>(`${GAME_PREFIX}/`, payload);
    return response.data;
}

export async function getGameState(): Promise<{ state: "idle" | "init" | "running" }> {
    const response = await api.get<{ state: "idle" | "init" | "running" }>(`${GAME_PREFIX}/state`);
    return response.data;
}

// Backend currently returns no body from /game/start.
export async function startGame(): Promise<void> {
    await api.post(`${GAME_PREFIX}/start`);
}

// Backend currently returns no body from /game/stop.
export async function stopGame(): Promise<void> {
    await api.post(`${GAME_PREFIX}/stop`);
}

// Backend /game/check is currently incomplete and may return empty body.
export async function checkGame(submission = ""): Promise<number | null> {
    const response = await api.post<number | null>(`${GAME_PREFIX}/check`, submission);
    return response.data ?? null;
}

export type { GameChangeRequest, GameResponse, GameResponseSafe };