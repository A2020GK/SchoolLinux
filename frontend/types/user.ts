export interface RegisterRequest {
	name: string;
	pcName: string;
}

export interface SafeUserData {
	name: string;
	pcName: string;
	score: number;
	kicked: boolean;
}

export interface UserResponse {
	isTeacher: boolean;
	user: SafeUserData | null;
}

export type UsersMap = Record<string, SafeUserData>;

export interface KickedEventPayload {
	kicked: boolean;
}
