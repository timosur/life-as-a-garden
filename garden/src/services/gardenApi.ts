import type { GardenData, PlantStatusChangesResponse, NotesResponse } from "../types/garden";

const getApiBaseUrl = () => {
  // If frontend is accessed from garden.timosur.com, use https://garden.timosur.com
  if (window.location.hostname === "garden.timosur.com") {
    return "https://garden.timosur.com";
  }

  // Otherwise, use http://localhost:8000
  return "http://localhost:8000";
};

const API_BASE_URL = getApiBaseUrl();

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

  async updateNote(
    noteId: number,
    content: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notes/${noteId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content }),
      });
      if (!response.ok) {
        throw new Error("Failed to update note");
      }
      return await response.json();
    } catch (error) {
      console.error("Error updating note:", error);
      return { success: false, error: String(error) };
    }
  },

  async createNote(noteData: { extracted_at: string; content: string }): Promise<{
    success: boolean;
    message?: string;
    error?: string;
    note?: {
      id: number;
      extracted_at: string;
      content: string;
      created_at: string;
      updated_at: string;
    };
  }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(noteData),
      });

      const result = await response.json();

      if (!response.ok) {
        return { success: false, error: result.error || "Failed to create note" };
      }

      return {
        success: true,
        message: result.message,
        note: result.note,
      };
    } catch (error) {
      console.error("Error creating note:", error);
      return { success: false, error: String(error) };
    }
  },

  // Plant CRUD operations
  async updatePlant(
    plantId: number,
    updates: Partial<{
      name: string;
      health: string;
      size: string;
      image_path: string;
      position: string;
      areal_id: string;
      last_watered: string;
      days_without_water: number;
      water_streak: number;
      total_water_count: number;
    }>
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/garden/plants/${plantId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updates),
      });

      const result = await response.json();

      if (!response.ok) {
        return { success: false, error: result.error || "Failed to update plant" };
      }

      return { success: true, message: result.message };
    } catch (error) {
      console.error("Error updating plant:", error);
      return { success: false, error: String(error) };
    }
  },

  async createPlant(plantData: {
    areal_id: string;
    name: string;
    health?: string;
    image_path?: string;
    size?: string;
    position?: string;
    days_without_water?: number;
    water_streak?: number;
    total_water_count?: number;
    last_watered?: string;
  }): Promise<{
    success: boolean;
    message?: string;
    error?: string;
    plant?: {
      id: number;
      name: string;
      health: string;
      image_path: string;
      size: string;
      position: string;
      areal_id: string;
    };
  }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/garden/plants`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(plantData),
      });

      const result = await response.json();

      if (!response.ok) {
        return { success: false, error: result.error || "Failed to create plant" };
      }

      return {
        success: true,
        message: result.message,
        plant: result.plant,
      };
    } catch (error) {
      console.error("Error creating plant:", error);
      return { success: false, error: String(error) };
    }
  },

  async deletePlant(
    plantId: number
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/garden/plants/${plantId}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (!response.ok) {
        return { success: false, error: result.error || "Failed to delete plant" };
      }

      return { success: true, message: result.message };
    } catch (error) {
      console.error("Error deleting plant:", error);
      return { success: false, error: String(error) };
    }
  },

  async movePlant(
    plantId: number,
    newArealId: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/garden/plants/${plantId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ areal_id: newArealId }),
      });

      const result = await response.json();

      if (!response.ok) {
        return { success: false, error: result.error || "Failed to move plant" };
      }

      return { success: true, message: result.message };
    } catch (error) {
      console.error("Error moving plant:", error);
      return { success: false, error: String(error) };
    }
  },

  // Areal CRUD operations
  async updateAreal(
    arealId: string,
    updates: Partial<{
      name: string;
      horizontal_pos: string;
      vertical_pos: string;
      size: string;
    }>
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/garden/areals/${arealId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updates),
      });

      const result = await response.json();

      if (!response.ok) {
        return { success: false, error: result.error || "Failed to update areal" };
      }

      return { success: true, message: result.message };
    } catch (error) {
      console.error("Error updating areal:", error);
      return { success: false, error: String(error) };
    }
  },

  async createAreal(arealData: {
    id: string;
    name: string;
    horizontal_pos: string;
    vertical_pos: string;
    size: string;
  }): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/garden/areals`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(arealData),
      });

      const result = await response.json();

      if (!response.ok) {
        return { success: false, error: result.error || "Failed to create areal" };
      }

      return { success: true, message: result.message };
    } catch (error) {
      console.error("Error creating areal:", error);
      return { success: false, error: String(error) };
    }
  },

  async deleteAreal(
    arealId: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/garden/areals/${arealId}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (!response.ok) {
        return { success: false, error: result.error || "Failed to delete areal" };
      }

      return { success: true, message: result.message };
    } catch (error) {
      console.error("Error deleting areal:", error);
      return { success: false, error: String(error) };
    }
  },
};
