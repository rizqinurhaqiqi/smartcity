import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const cctvService = {
  getAllCCTV: () => apiClient.get('/cctv'),
  getCCTVDetail: (cctvId) => apiClient.get(`/cctv/${cctvId}`),
};

export const trafficService = {
  analyzeCCTV: (cctvId) => apiClient.get(`/analyze/${cctvId}?t=${Date.now()}`),
  getHistory: (cctvId, hours = 24) =>
    apiClient.get(`/analyze/history/${cctvId}?hours=${hours}`),
  getLatestAnalysis: () => apiClient.get('/analyze/latest'),
};

export const healthService = {
  checkHealth: () => apiClient.get('/health'),
};

export default apiClient;