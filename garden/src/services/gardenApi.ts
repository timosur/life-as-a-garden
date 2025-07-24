import type { GardenData, PlantStatusChangesResponse } from "../types/garden";

// API-Service für echte REST API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const GardenApiService = {
  async getGardenData(): Promise<GardenData | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/garden`);
      if (!response.ok) {
        throw new Error("Failed to fetch garden data");
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching garden data:", error);
      // Fallback to local data if API is not available
      return null;
    }
  },

  async getPlantStatusChanges(
    plantId?: number,
    limit?: number
  ): Promise<PlantStatusChangesResponse | null> {
    try {
      const params = new URLSearchParams();
      if (plantId) params.append("plant_id", plantId.toString());
      if (limit) params.append("limit", limit.toString());

      const url = `${API_BASE_URL}/api/garden/plant-status-changes${
        params.toString() ? "?" + params.toString() : ""
      }`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error("Failed to fetch plant status changes");
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching plant status changes:", error);
      return null;
    }
  },

  async getTodaysChanges(): Promise<PlantStatusChangesResponse | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/garden/plant-status-changes/today`);

      if (!response.ok) {
        throw new Error("Failed to fetch today's plant status changes");
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching today's changes:", error);
      return null;
    }
  },
};
