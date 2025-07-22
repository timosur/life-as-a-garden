import type { Plant, GardenData, HealthTint } from "../types/garden";
import { getCanvasConfig, getArealCoordinatesWithSize, getPlantPosition } from "./geometry";
import { loadPlantImage, getCachedImage, setCachedImage } from "./imageUtils";

// Funktion zur Generierung von Pflanzen basierend auf Garden-Daten
export const generatePlantsFromData = async (
  data: GardenData,
  canvasWidth: number,
  canvasHeight: number
): Promise<Plant[]> => {
  const config = getCanvasConfig(canvasWidth);
  const plants: Plant[] = [];

  for (const areal of data.areals) {
    const arealCoords = getArealCoordinatesWithSize(
      areal.horizontalPos,
      areal.verticalPos,
      config.areal.radius,
      canvasHeight,
      config.path,
      areal.size
    );

    for (const plantConfig of areal.plants) {
      // Load image dynamically with caching
      let imageSrc = getCachedImage(plantConfig.imagePath);
      if (!imageSrc) {
        imageSrc = await loadPlantImage(plantConfig.imagePath);
        setCachedImage(plantConfig.imagePath, imageSrc);
      }

      const plantPosition = getPlantPosition(
        arealCoords.x,
        arealCoords.y,
        arealCoords.radius,
        plantConfig.size,
        plantConfig.position
      );

      const plant: Plant = {
        name: plantConfig.name,
        health: plantConfig.health,
        src: imageSrc,
        x: plantPosition.x,
        y: plantPosition.y,
        size: plantConfig.size,
      };

      plants.push(plant);
    }
  }

  return plants;
};

export const getHealthTint = (health: Plant["health"]): HealthTint => {
  switch (health) {
    case "healthy":
      return { r: 0, g: 255, b: 0, alpha: 0.2 }; // Green tint
    case "okay":
      return { r: 255, g: 255, b: 0, alpha: 0.3 }; // Yellow tint
    case "dead":
      return { r: 255, g: 0, b: 0, alpha: 0.4 }; // Red tint
    default:
      return { r: 0, g: 0, b: 0, alpha: 0 };
  }
};

// Helper functions for plant visualization
export const getPlantSize = (size: Plant["size"]) => {
  switch (size) {
    case "small":
      return 40;
    case "medium":
      return 60;
    case "big":
      return 80;
    default:
      return 60;
  }
};
