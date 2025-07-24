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

export interface PlantStatusChange {
  id: number;
  plant_id: number;
  plant_name: string;
  change_date: string;
  change_type: "watered" | "daily_update";
  old_health: string;
  new_health: string;
  old_growth_stage: number;
  new_growth_stage: number;
  old_water_streak: number;
  new_water_streak: number;
  old_days_without_water: number;
  new_days_without_water: number;
  old_total_water_count: number;
  new_total_water_count: number;
  created_at: string;
}

export interface PlantStatusChangesResponse {
  success: boolean;
  status_changes: PlantStatusChange[];
  error?: string;
}
