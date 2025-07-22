import type { GardenData } from "../types/garden";

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
};
