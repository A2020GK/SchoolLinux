import type { GameResponse } from "../types/game";
import type { SafeUserData, UserResponse, UsersMap } from "../types/user";

export type MockPreviewScreen = "student-login" | "student-content" | "teacher";
type MockGameState = "idle" | "init" | "running" | "stopped";

interface MockPreviewConfig {
    enabled: boolean;
    screen: MockPreviewScreen;
    student: SafeUserData;
    users: UsersMap;
    currentGame: GameResponse;
    gamesList: Record<string, GameResponse>;
    gameState: MockGameState;
}

interface FrontendEnvConfig {
    apiBaseUrl: string;
    mockPreview: MockPreviewConfig;
}

const DEFAULT_API_BASE_URL = `http://${location.hostname}:8000`;

const parseBoolean = (value: string | undefined, fallback = false): boolean => {
    if (value === undefined) return fallback;
    return ["1", "true", "yes", "on"].includes(value.toLowerCase());
};

const parseNumber = (value: string | undefined, fallback: number): number => {
    if (value === undefined) return fallback;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
};

const parsePreviewScreen = (value: string | undefined): MockPreviewScreen => {
    if (value === "teacher" || value === "student-login" || value === "student-content") {
        return value;
    }
    return "student-content";
};

const student: SafeUserData = {
    name: import.meta.env.VITE_MOCK_STUDENT_NAME ?? "Тест Тестовский",
    pcName: import.meta.env.VITE_MOCK_STUDENT_PC ?? "403-1",
    score: parseNumber(import.meta.env.VITE_MOCK_STUDENT_SCORE, 12),
    kicked: false,
};

const currentGame: GameResponse = {
    name: "Поиск клада",
    description: "Найдите скрытый файл с ключом и отправьте его содержимое.",
    stringSubmission: true,
    requiredUserScore: 5,
    anticheatRequired: false,
    settings: {
        baseDir: "$HOME",
        hintsEnabled: true,
        maxAttempts: 3,
    },
    settingsForm: {
        baseDir: {
            name: "Базовая папка",
            type: "string",
            options: null,
            default: "$HOME",
            value: "$HOME",
        },
        hintsEnabled: {
            name: "Подсказки",
            type: "boolean",
            options: null,
            default: true,
            value: true,
        },
        maxAttempts: {
            name: "Максимум попыток",
            type: "number",
            options: null,
            default: 3,
            value: 3,
        },
    },
};

const gamesList: Record<string, GameResponse> = {
    find: currentGame,
    hide: {
        ...currentGame,
        name: "Спрячь файл",
        description: "Создайте файл по условию и правильно выставьте права доступа.",
    },
};

const mockPreview: MockPreviewConfig = {
    enabled: parseBoolean(import.meta.env.VITE_MOCK_PREVIEW, false),
    screen: parsePreviewScreen(import.meta.env.VITE_MOCK_SCREEN),
    student,
    users: {
        "192.168.0.11": student,
        "192.168.0.12": {
            name: "Иван Петров",
            pcName: "403-2",
            score: 8,
            kicked: false,
        },
        "192.168.0.13": {
            name: "Мария Сидорова",
            pcName: "403-3",
            score: 15,
            kicked: true,
        },
    },
    currentGame,
    gamesList,
    gameState: "idle",
};

export const frontendEnv: FrontendEnvConfig = {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL,
    mockPreview,
};

export const getMockUserResponse = (): UserResponse => {
    if (frontendEnv.mockPreview.screen === "teacher") {
        return {
            isTeacher: true,
            user: null,
        };
    }

    if (frontendEnv.mockPreview.screen === "student-login") {
        return {
            isTeacher: false,
            user: null,
        };
    }

    return {
        isTeacher: false,
        user: frontendEnv.mockPreview.student,
    };
};
