import { api } from "./api";
import type {
	RegisterRequest,
	SafeUserData,
	UserResponse,
	UsersMap,
} from "../types/user";

const USER_PREFIX = "/user";

export async function registerUser(payload: RegisterRequest): Promise<UserResponse> {
	const response = await api.post<UserResponse>(`${USER_PREFIX}/register`, payload);
	return response.data;
}

export async function getCurrentUser(): Promise<UserResponse> {
	const response = await api.get<UserResponse>(`${USER_PREFIX}/me`);
	return response.data;
}

export async function getAllUsers(): Promise<UsersMap> {
	const response = await api.get<UsersMap>(`${USER_PREFIX}/all`);
	return response.data;
}

export async function setUserKicked(ip: string, kicked: boolean): Promise<SafeUserData> {
	const response = await api.post<SafeUserData>(`${USER_PREFIX}/kick/${encodeURIComponent(ip)}`, kicked);
	return response.data;
}

export async function deleteCurrentUser(): Promise<{ deleted: boolean }> {
	const response = await api.delete<{ deleted: boolean }>(`${USER_PREFIX}/me`);
	return response.data;
}

export type { RegisterRequest, SafeUserData, UserResponse, UsersMap };

