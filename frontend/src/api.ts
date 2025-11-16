import axios from "axios";
import { io } from "socket.io-client";

const apiBaseUrl = `http://${location.hostname}:8000/`

export const api = axios.create({
    baseURL:`${apiBaseUrl}/`
})

export const socket = io(apiBaseUrl, {autoConnect:true})
