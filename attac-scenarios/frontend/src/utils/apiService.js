const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

export const apiService = {
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch (error) {
      console.error("API health check failed:", error);
      return false;
    }
  },

  async fetchCompletedScenarios() {
    try {
      const response = await fetch(
        `${API_BASE_URL}/scenarios/status/completed`
      );
      if (response.ok) {
        const data = await response.json();
        return data.data || [];
      }
      return [];
    } catch (error) {
      console.error("Failed to fetch completed scenarios:", error);
      return [];
    }
  },

  async saveScenario(scenario) {
    try {
      const scenarioData = {
        scenarioId: `SC${scenario.id.toString().padStart(3, "0")}`,
        title: `Attack Scenario ${scenario.id} - ${scenario.type}`,
        description: `${scenario.type} attack scenario with ${
          Object.keys(scenario).filter(
            (key) => key !== "id" && key !== "type" && scenario[key]
          ).length
        } attack steps`,
        attackTechniques: Object.entries(scenario)
          .filter(([key, value]) => key !== "id" && key !== "type" && value)
          .map(([key, value]) => ({
            techniqueId: `T${Math.floor(1000 + Math.random() * 9000)}`,
            techniqueName: value,
            tactic: key,
          })),
      };

      const response = await fetch(`${API_BASE_URL}/scenarios`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(scenarioData),
      });

      return response.ok || response.status === 409; // 409 means already exists
    } catch (error) {
      console.error("Failed to save scenario:", error);
      return false;
    }
  },

  async markScenarioComplete(scenarioId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/scenarios/${scenarioId}/complete`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      return response.ok;
    } catch (error) {
      console.error("Failed to mark scenario as complete:", error);
      return false;
    }
  },

  async markScenarioIncomplete(scenarioId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/scenarios/${scenarioId}/incomplete`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      return response.ok;
    } catch (error) {
      console.error("Failed to mark scenario as incomplete:", error);
      return false;
    }
  },
};
