import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const logService = {
  async analyzeLog(logContent, sessionId = null) {
    const response = await api.post("/api/logs/analyze", {
      log_content: logContent,
      session_id: sessionId,
    });
    return response.data;
  },

  async getAnalysis(analysisId) {
    const response = await api.get(`/api/logs/history/${analysisId}`);
    return response.data;
  },

  async getSessionAnalyses(sessionId) {
    const response = await api.get(`/api/logs/session/${sessionId}`);
    return response.data;
  },

  async getRecentAnalyses(limit = 10) {
    const response = await api.get("/api/logs/recent", {
      params: { limit },
    });
    return response.data;
  },

  async getStats() {
    const response = await api.get("/api/logs/stats");
    return response.data;
  },

  async healthCheck() {
    const response = await api.get("/api/logs/health");
    return response.data;
  },
};

export default api;
