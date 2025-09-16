import { useState, useEffect } from "react";
import { apiService } from "../utils/apiService";

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");
  const [completedScenarios, setCompletedScenarios] = useState([]);

  const checkApiStatus = async () => {
    const isConnected = await apiService.checkHealth();
    setApiStatus(isConnected ? "connected" : "disconnected");
  };

  const fetchCompletedScenarios = async () => {
    setLoading(true);
    const scenarios = await apiService.fetchCompletedScenarios();
    setCompletedScenarios(scenarios);
    setLoading(false);
  };

  const saveScenarioToDatabase = async (scenario) => {
    setLoading(true);
    const success = await apiService.saveScenario(scenario);
    setLoading(false);
    return success;
  };

  const markScenarioComplete = async (scenarioId) => {
    setLoading(true);
    const success = await apiService.markScenarioComplete(scenarioId);
    if (success) {
      await fetchCompletedScenarios();
    }
    setLoading(false);
    return success;
  };

  const markScenarioIncomplete = async (scenarioId) => {
    setLoading(true);
    const success = await apiService.markScenarioIncomplete(scenarioId);
    if (success) {
      await fetchCompletedScenarios();
    }
    setLoading(false);
    return success;
  };

  useEffect(() => {
    checkApiStatus();
    fetchCompletedScenarios();
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return {
    loading,
    apiStatus,
    completedScenarios,
    fetchCompletedScenarios,
    saveScenarioToDatabase,
    markScenarioComplete,
    markScenarioIncomplete,
  };
};
