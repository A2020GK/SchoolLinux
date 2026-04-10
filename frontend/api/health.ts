import { api } from "./api";
import type { PingResponse } from "../types/health";

export async function ping(): Promise<PingResponse> {
    const response = await api.get<PingResponse>("/ping");
    return response.data;
}

export type { PingResponse };