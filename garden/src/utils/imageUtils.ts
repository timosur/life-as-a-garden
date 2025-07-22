import type { GardenData } from "../types/garden";

// Cache for loaded images to avoid re-importing
const imageCache: { [key: string]: string } = {};

// Dynamic plant image loader
export const loadPlantImage = async (imagePath: string): Promise<string> => {
  try {
    const module = await import(`../assets/plants/${imagePath}.png`);
    return module.default;
  } catch (error) {
    console.error(`Failed to load plant image: ${imagePath}`, error);
    // Return a fallback or empty string
    return "";
  }
};

// Utility function to get all unique plant images from garden data
export const getUniqueImagePaths = (data: GardenData): string[] => {
  const imagePaths = new Set<string>();
  data.areals.forEach((areal) => {
    areal.plants.forEach((plant) => {
      imagePaths.add(plant.imagePath);
    });
  });
  return Array.from(imagePaths);
};

// Utility function to preload all images for better performance
export const preloadPlantImages = async (data: GardenData): Promise<void> => {
  const uniqueImagePaths = getUniqueImagePaths(data);
  const loadPromises = uniqueImagePaths.map(async (imagePath) => {
    if (!imageCache[imagePath]) {
      const imageSrc = await loadPlantImage(imagePath);
      imageCache[imagePath] = imageSrc;
    }
  });

  await Promise.all(loadPromises);
};

// Get cached image
export const getCachedImage = (imagePath: string): string | undefined => {
  return imageCache[imagePath];
};

// Set cached image
export const setCachedImage = (imagePath: string, imageSrc: string): void => {
  imageCache[imagePath] = imageSrc;
};
