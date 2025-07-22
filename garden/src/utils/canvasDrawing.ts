import type { Plant, GardenData } from "../types/garden";
import { getCanvasConfig, getArealCoordinates, getArealSize } from "./geometry";
import { getPlantSize, getHealthTint } from "./plantUtils";

// Funktion zum Zeichnen des Hauptweges
export const drawPath = (
  ctx: CanvasRenderingContext2D,
  pathConfig: { x: number; width: number },
  canvasHeight: number
) => {
  // Hauptweg zeichnen
  ctx.fillStyle = "#D3D3D3";
  ctx.fillRect(pathConfig.x, 0, pathConfig.width, canvasHeight);

  // Weg-Ränder
  ctx.strokeStyle = "#8B4513";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(pathConfig.x, 0);
  ctx.lineTo(pathConfig.x, canvasHeight);
  ctx.moveTo(pathConfig.x + pathConfig.width, 0);
  ctx.lineTo(pathConfig.x + pathConfig.width, canvasHeight);
  ctx.stroke();

  // Eingangstor am unteren Ende
  const gateWidth = pathConfig.width;
  const gateHeight = canvasHeight * 0.0375;
  ctx.fillStyle = "#8B4513";
  ctx.fillRect(pathConfig.x - gateWidth / 2, canvasHeight - gateHeight, gateWidth, gateHeight);
  ctx.fillRect(
    pathConfig.x + pathConfig.width - gateWidth / 2,
    canvasHeight - gateHeight,
    gateWidth,
    gateHeight
  );
};

// Funktion zum Zeichnen aller Areale basierend auf Garden-Daten
export const drawArealsFromData = (
  ctx: CanvasRenderingContext2D,
  data: GardenData,
  canvasWidth: number,
  canvasHeight: number,
  pathConfig: { x: number; width: number }
) => {
  data.areals.forEach((areal) => {
    const config = getCanvasConfig(canvasWidth);
    drawAreal(
      ctx,
      areal.horizontalPos,
      areal.verticalPos,
      config.areal.radius,
      areal.name,
      canvasWidth,
      canvasHeight,
      pathConfig,
      areal.size
    );
  });
};

// Funktion zum Zeichnen eines Areals mit automatischem Verbindungsweg
export const drawAreal = (
  ctx: CanvasRenderingContext2D,
  horizontalPos: "left" | "right",
  verticalPos: "top" | "middle" | "bottom",
  baseRadius: number,
  label: string,
  canvasWidth: number,
  canvasHeight: number,
  pathConfig: { x: number; width: number },
  size: "small" | "medium" | "large" = "large"
) => {
  // Tatsächliche Radius basierend auf Size berechnen
  const radius = getArealSize(size, baseRadius);

  // Koordinaten basierend auf Position berechnen
  const { x, y } = getArealCoordinates(
    horizontalPos,
    verticalPos,
    radius,
    canvasHeight,
    pathConfig
  );

  // Areal zeichnen (rund)
  ctx.fillStyle = "#d0f0c0";
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.fill();

  // Areal-Rand zeichnen
  ctx.strokeStyle = "#8B4513";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.stroke();

  // Areal-Beschriftung
  ctx.fillStyle = "#000";
  ctx.font = `${canvasWidth * 0.02}px sans-serif`; // 2% der Canvas-Breite
  ctx.textAlign = "center";
  const labelOffset = radius + 30;
  ctx.fillText(label, x, y + labelOffset);

  // Verbindungsweg zum Hauptweg zeichnen
  const connectionWidth = pathConfig.width * 1.6;
  const connectionHeight = canvasHeight * 0.025;
  const connectionY = y - connectionHeight / 2;

  ctx.fillStyle = "#D3D3D3";

  if (horizontalPos === "left") {
    // Weg von links zum Hauptweg
    ctx.fillRect(pathConfig.x - connectionWidth, connectionY, connectionWidth, connectionHeight);

    // Ränder für Verbindungsweg
    ctx.strokeStyle = "#8B4513";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(pathConfig.x - connectionWidth, connectionY);
    ctx.lineTo(pathConfig.x, connectionY);
    ctx.moveTo(pathConfig.x - connectionWidth, connectionY + connectionHeight);
    ctx.lineTo(pathConfig.x, connectionY + connectionHeight);
    ctx.stroke();
  } else {
    // Weg von rechts zum Hauptweg
    ctx.fillRect(pathConfig.x + pathConfig.width, connectionY, connectionWidth, connectionHeight);

    // Ränder für Verbindungsweg
    ctx.strokeStyle = "#8B4513";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(pathConfig.x + pathConfig.width, connectionY);
    ctx.lineTo(pathConfig.x + pathConfig.width + connectionWidth, connectionY);
    ctx.moveTo(pathConfig.x + pathConfig.width, connectionY + connectionHeight);
    ctx.lineTo(pathConfig.x + pathConfig.width + connectionWidth, connectionY + connectionHeight);
    ctx.stroke();
  }
};

export const drawLegend = (ctx: CanvasRenderingContext2D) => {
  // Add legend for plant health and size
  const legendX = 50;
  const legendY = 50;
  const legendWidth = 200;
  const legendHeight = 120;

  // Legend background
  ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
  ctx.fillRect(legendX, legendY, legendWidth, legendHeight);
  ctx.strokeStyle = "#333";
  ctx.lineWidth = 1;
  ctx.strokeRect(legendX, legendY, legendWidth, legendHeight);

  // Legend title
  ctx.fillStyle = "#333";
  ctx.font = "bold 16px sans-serif";
  ctx.textAlign = "left";
  ctx.fillText("Legende", legendX + 10, legendY + 20);

  // Health indicators
  ctx.font = "12px sans-serif";
  const healthItems = [
    { emoji: "😊", text: "Gesund" },
    { emoji: "😐", text: "Okay" },
    { emoji: "😵", text: "Braucht Hilfe" },
  ];

  healthItems.forEach((item, index) => {
    const y = legendY + 40 + index * 20;

    // Emoji indicator
    ctx.font = "16px sans-serif";
    ctx.textAlign = "center";
    ctx.fillStyle = "#000";
    ctx.fillText(item.emoji, legendX + 15, y + 4);

    // Text
    ctx.font = "12px sans-serif";
    ctx.textAlign = "left";
    ctx.fillStyle = "#333";
    ctx.fillText(item.text, legendX + 30, y + 4);
  });

  // Size info
  ctx.fillText("6x Gießen / Tag", legendX + 10, legendY + 110);
};

export const drawPlantWithEffects = (ctx: CanvasRenderingContext2D, img: string, plant: Plant) => {
  const size = getPlantSize(plant.size);
  const tint = getHealthTint(plant.health);

  const image = new Image();
  image.src = img;

  image.onload = () => {
    // Draw the plant image after it has loaded
    ctx.drawImage(image, plant.x, plant.y, size, size);

    // Apply health tint overlay
    if (tint.alpha > 0) {
      ctx.globalCompositeOperation = "source-atop";
      ctx.fillStyle = `rgba(${tint.r}, ${tint.g}, ${tint.b}, ${tint.alpha})`;
      ctx.fillRect(plant.x, plant.y, size, size);
      ctx.globalCompositeOperation = "source-over";
    }

    // Add health indicator (emoji)
    const indicatorX = plant.x + size;
    const indicatorY = plant.y + 15;

    ctx.font = "20px sans-serif";
    ctx.textAlign = "center";

    let emoji;
    switch (plant.health) {
      case "healthy":
        emoji = "😊"; // Happy face
        break;
      case "okay":
        emoji = "😐"; // Neutral face
        break;
      case "dead":
        emoji = "😵"; // Dizzy/dead face
        break;
    }

    ctx.fillStyle = "#000";
    ctx.fillText(emoji, indicatorX, indicatorY);

    // Plant name (positioned based on plant size)
    ctx.fillStyle = "#000";
    ctx.font = "14px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(plant.name, plant.x + size / 2, plant.y - 8);
  };
};
