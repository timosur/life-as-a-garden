import { useEffect, useRef } from 'react';
import type { Plant, GardenData } from '../types/garden';
import { getCanvasConfig } from '../utils/geometry';
import { drawPath, drawArealsFromData, drawPlantWithEffects, drawLegend } from '../utils/canvasDrawing';

interface GardenCanvasProps {
  gardenConfig: GardenData;
  plants: Plant[];
  width: number;
  height: number;
}

export const GardenCanvas: React.FC<GardenCanvasProps> = ({
  gardenConfig,
  plants,
  width,
  height
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Canvas-basierte Konfiguration berechnen
    const canvasConfig = getCanvasConfig(canvas.width);

    // Hauptweg zeichnen
    drawPath(ctx, canvasConfig.path, canvas.height);

    // Areale mit Verbindungswegen zeichnen (basierend auf JSON-Daten)
    drawArealsFromData(ctx, gardenConfig, canvas.width, canvas.height, canvasConfig.path);

    // Place plants in the garden areas
    plants.forEach(plant => {
      drawPlantWithEffects(ctx, plant.src, plant);
    });

    // Draw the legend
    drawLegend(ctx);
  }, [gardenConfig, plants, width, height]);

  return <canvas ref={canvasRef} width={width} height={height} />;
};
