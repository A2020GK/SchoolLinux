import axios from "axios";
import { io } from "socket.io-client";
import { frontendEnv } from "../config/env";

const apiBaseUrl = frontendEnv.apiBaseUrl;

export const api = axios.create({
    baseURL: `${apiBaseUrl}/`,
    timeout: 10000,
    headers: {
        "Content-Type": "application/json",
    },
});

export const socket = io(apiBaseUrl, {
    autoConnect: true,
    transports: ["websocket"],
});

export { apiBaseUrl };
