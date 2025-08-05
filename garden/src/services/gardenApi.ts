import type { GardenData, PlantStatusChangesResponse, NotesResponse } from "../types/garden";

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

  async getAllNotes(): Promise<NotesResponse | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notes`);
      if (!response.ok) {
        throw new Error("Failed to fetch notes");
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching notes:", error);
      return null;
    }
  },

  async getNotesByDate(date: string): Promise<NotesResponse | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notes/date/${date}`);
      if (!response.ok) {
        throw new Error("Failed to fetch notes for date");
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching notes by date:", error);
      return null;
    }
  },

  async getNotesByDateRange(startDate: string, endDate: string): Promise<NotesResponse | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notes/range/${startDate}/${endDate}`);
      if (!response.ok) {
        throw new Error("Failed to fetch notes for date range");
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching notes by date range:", error);
      return null;
    }
  },

  async deleteNote(
    noteId: number
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notes/${noteId}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error("Failed to delete note");
      }
      return await response.json();
    } catch (error) {
      console.error("Error deleting note:", error);
      return { success: false, error: String(error) };
    }
  },
};
