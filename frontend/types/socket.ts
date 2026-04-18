import type { GameResponseSafe } from "./game";
import type { KickedEventPayload, SafeUserData, UsersMap } from "./user";

export interface ServerToClientEvents {
    users_update: (users: UsersMap) => void;
    user_update: (user: SafeUserData) => void;
    kicked: (payload: KickedEventPayload) => void;
    game_change: (game: GameResponseSafe) => void;
    game_state_changed: (payload: { state: "idle" | "init" | "running" }) => void;
}

export interface ClientToServerEvents {
    // Reserved for future client-emitted events.
}

export type SocketEventName = keyof ServerToClientEvents;