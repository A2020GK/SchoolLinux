import type { GameResponseSafe } from "./game";
import type { KickedEventPayload, UsersMap } from "./user";

export interface ServerToClientEvents {
    users_update: (users: UsersMap) => void;
    kicked: (payload: KickedEventPayload) => void;
    game_change: (game: GameResponseSafe) => void;
}

export interface ClientToServerEvents {
    // Reserved for future client-emitted events.
}

export type SocketEventName = keyof ServerToClientEvents;