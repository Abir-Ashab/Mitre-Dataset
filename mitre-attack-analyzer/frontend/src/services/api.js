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

// Session Service - for uploading full session logs
export const sessionService = {
  async uploadSession(logContent, sessionId, sessionName = null) {
    const response = await api.post("/api/logs/sessions/upload", {
      log_content: logContent,
      session_id: sessionId,
      session_name: sessionName,
    });
    return response.data;
  },

  async getAllSessions(skip = 0, limit = 20) {
    const response = await api.get("/api/logs/sessions", {
      params: { skip, limit },
    });
    return response.data;
  },

  async getSessionDetails(sessionId, skip = 0, limit = 50) {
    const response = await api.get(`/api/logs/sessions/${sessionId}`, {
      params: { skip, limit },
    });
    return response.data;
  },

  async getChunkData(sessionId, chunkIndex) {
    const response = await api.get(
      `/api/logs/sessions/${sessionId}/chunks/${chunkIndex}`,
    );
    return response.data;
  },

  async deleteSession(sessionId) {
    const response = await api.delete(`/api/logs/sessions/${sessionId}`);
    return response.data;
  },
};

export default api;
