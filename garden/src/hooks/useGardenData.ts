import { useState, useEffect } from "react";
import type { GardenData, Plant } from "../types/garden";
import { GardenApiService } from "../services/gardenApi";
import { preloadPlantImages } from "../utils/imageUtils";
import { generatePlantsFromData } from "../utils/plantUtils";

interface UseGardenDataReturn {
  gardenConfig: GardenData | null;
  plants: Plant[];
  loading: boolean;
  error: string | null;
}

export const useGardenData = (
  canvasWidth: number = 1100,
  canvasHeight: number = 1400
): UseGardenDataReturn => {
  const [gardenConfig, setGardenConfig] = useState<GardenData | null>(null);
  const [plants, setPlants] = useState<Plant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGardenData = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await GardenApiService.getGardenData();
        setGardenConfig(data);

        if (!data) {
          throw new Error("No garden data available");
        }

        // Preload all images for better performance
        await preloadPlantImages(data);

        // Generate plants with dynamic image loading
        const generatedPlants = await generatePlantsFromData(data, canvasWidth, canvasHeight);
        setPlants(generatedPlants);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Unknown error occurred";
        console.error("Fehler beim Laden der Gartendaten:", err);
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchGardenData();
  }, [canvasWidth, canvasHeight]);

  return {
    gardenConfig,
    plants,
    loading,
    error,
  };
};
