export interface Plant {
  x: number;
  y: number;
  name: string;
  src: string;
  health: "healthy" | "okay" | "dead";
  size: "small" | "medium" | "big";
}

export interface PlantConfig {
  name: string;
  health: "healthy" | "okay" | "dead";
  imagePath: string;
  size: "small" | "medium" | "big";
  position: string;
}

export interface ArealConfig {
  id: string;
  name: string;
  horizontalPos: "left" | "right";
  verticalPos: "top" | "middle" | "bottom";
  size: "small" | "medium" | "large";
  plants: PlantConfig[];
}

export interface GardenData {
  areals: ArealConfig[];
}

export interface CanvasConfig {
  areal: {
    radius: number;
  };
  path: {
    width: number;
    x: number;
  };
}

export interface HealthTint {
  r: number;
  g: number;
  b: number;
  alpha: number;
}
