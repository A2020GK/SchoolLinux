export type GameSettingType = "string" | "number" | "boolean" | "option";

export interface GameSettingsItem {
    name: string;
    type: GameSettingType;
    options: Record<string, string> | null;
    default: string | number | boolean;
    value: string | number | boolean | null;
}

export interface GameResponseSafe {
    name: string;
    description: string;
    stringSubmission: boolean;
    requiredUserScore: number;
    settings: Record<string, string | number | boolean>;
}

export interface GameResponse extends GameResponseSafe {
    anticheatRequired: boolean;
    settingsForm: Record<string, GameSettingsItem>;
}

export interface GameChangeRequest {
    gameKey: string;
    settings?: Record<string, string | number | boolean>;
}