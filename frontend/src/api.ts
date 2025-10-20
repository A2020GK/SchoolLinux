import axios from 'axios';
import { Status, PCData, RegPCRequest, APIResponse } from './types';

// API configuration
export const apiAddr = `${location.hostname}:8000`;
export const apiBase = `http://${apiAddr}`;

// Create axios instance with base configuration
const api = axios.create({
  baseURL: apiBase,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const apiService = {
  // Get current status
  getStatus: async (): Promise<Status> => {
    const response = await api.get('/status');
    return response.data;
  },

  // Register a PC
  registerPC: async (data: RegPCRequest): Promise<APIResponse> => {
    const response = await api.post('/pcs/reg', data);
    return response.data;
  },

  // Get all PCs
  getPCs: async (): Promise<PCData> => {
    const response = await api.get('/pcs');
    return response.data;
  },

  // Delete a PC by IP
  deletePC: async (ip: string): Promise<APIResponse<PCData>> => {
    const response = await api.delete(`/pcs/${ip}`);
    return response.data;
  },
};

export default api;
