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
  old_size: string;
  new_size: string;
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

export interface Note {
  id: number;
  content: string;
  extracted_at: string;
  created_at: string;
  updated_at: string;
}

export interface NotesResponse {
  success: boolean;
  notes: Note[];
  error?: string;
  date?: string;
  start_date?: string;
  end_date?: string;
}

export interface WateringCalendarEntry {
  watering_date: string;
  plant_name: string;
  plant_id: number;
}

export interface WateringCalendarResponse {
  success: boolean;
  watering_history: WateringCalendarEntry[];
  start_date: string;
  end_date: string;
  count: number;
  error?: string;
}
