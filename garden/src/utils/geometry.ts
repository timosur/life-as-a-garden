import type { Plant, CanvasConfig } from "../types/garden";

const getPlantSize = (size: Plant["size"]) => {
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

// Funktion zur Berechnung der Canvas-abhängigen Konfiguration
export const getCanvasConfig = (canvasWidth: number): CanvasConfig => {
  const arealRadius = canvasWidth * 0.18; // 18% der Canvas-Breite
  const pathWidth = canvasWidth * 0.025; // 2.5% der Canvas-Breite
  const pathX = (canvasWidth - pathWidth) / 2;

  return {
    areal: {
      radius: arealRadius,
    },
    path: {
      width: pathWidth,
      x: pathX,
    },
  };
};

// Funktion zur Berechnung der Areal-Koordinaten basierend auf Position
export const getArealCoordinates = (
  horizontalPos: "left" | "right",
  verticalPos: "top" | "middle" | "bottom",
  radius: number,
  canvasHeight: number,
  pathConfig: { x: number; width: number }
) => {
  let x: number, y: number;

  // X-Koordinate berechnen - dynamischer Abstand basierend auf Radius
  const minDistance = radius + pathConfig.width * 1.65; // Mindestabstand = Radius + halbe Pfadbreite

  if (horizontalPos === "left") {
    x = pathConfig.x - minDistance; // Links vom Weg
  } else {
    x = pathConfig.x + pathConfig.width + minDistance; // Rechts vom Weg
  }

  // Y-Koordinate berechnen
  switch (verticalPos) {
    case "top":
      y = canvasHeight * 0.15;
      break;
    case "middle":
      y = canvasHeight * 0.45;
      break;
    case "bottom":
      y = canvasHeight * 0.81;
      break;
  }

  return { x, y };
};

// Funktion zur Berechnung der Areal-Größe basierend auf Size-Parameter
export const getArealSize = (size: "small" | "medium" | "large", baseRadius: number) => {
  switch (size) {
    case "small":
      return baseRadius * 0.6; // 60% der Basis-Größe
    case "medium":
      return baseRadius * 0.8; // 80% der Basis-Größe
    case "large":
      return baseRadius; // 100% der Basis-Größe (Standard)
    default:
      return baseRadius;
  }
};

// Hilfsfunktion zur Berechnung der Areal-Koordinaten mit Size für Pflanzen-Positionierung
export const getArealCoordinatesWithSize = (
  horizontalPos: "left" | "right",
  verticalPos: "top" | "middle" | "bottom",
  baseRadius: number,
  canvasHeight: number,
  pathConfig: { x: number; width: number },
  size: "small" | "medium" | "large" = "large"
) => {
  const radius = getArealSize(size, baseRadius);
  return {
    ...getArealCoordinates(horizontalPos, verticalPos, radius, canvasHeight, pathConfig),
    radius,
  };
};

export const getPlantPosition = (
  arealX: number,
  arealY: number,
  radius: number,
  plantSizeStr: Plant["size"],
  position: string
): { x: number; y: number; size: Plant["size"] } => {
  const plantSize = getPlantSize(plantSizeStr);
  const arealXMid = arealX - plantSize / 2;
  const arealYMid = arealY - plantSize / 2;

  const result = { x: arealXMid, y: arealYMid, size: plantSizeStr };

  switch (position) {
    case "top":
      result.x = arealXMid;
      result.y = arealYMid - radius * 0.6;
      break;
    case "bottom":
      result.x = arealXMid;
      result.y = arealYMid + radius * 0.6;
      break;
    case "left":
      result.x = arealX - radius * 0.8;
      result.y = arealYMid;
      break;
    case "right":
      result.x = arealX + radius * 0.4;
      result.y = arealYMid;
      break;
    case "top-left":
      result.x = arealX - radius * 0.6;
      result.y = arealYMid - radius * 0.6;
      break;
    case "top-right":
      result.x = arealX + radius * 0.6;
      result.y = arealYMid - radius * 0.6;
      break;
    case "bottom-left":
      result.x = arealX - radius * 0.4;
      result.y = arealYMid + radius * 0.6;
      break;
    case "bottom-right":
      result.x = arealXMid + radius * 0.4;
      result.y = arealYMid + radius * 0.6;
      break;
    case "center":
      result.x = arealXMid;
      result.y = arealYMid;
      break;
    case "center-top-mid":
      result.x = arealXMid;
      result.y = arealYMid - radius * 0.1;
      break;
    default:
      break;
  }

  return result;
};
