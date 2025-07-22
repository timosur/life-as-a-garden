import { useEffect, useRef } from 'react';
import type { Plant } from '../types/garden';

interface WateringPlanCanvasProps {
  plants: Plant[];
  width: number;
  height: number;
}

// Gießplan zeichnen
const drawWateringPlan = (wateringCtx: CanvasRenderingContext2D, plants: Plant[]) => {
  // Pflanzen-Liste
  const startY = 90;
  const itemHeight = 50;
  const checkboxSize = 20;
  const leftMargin = 50;
  const maxItemsPerColumn = 8;
  const columnWidth = 300; // Breite jeder Spalte

  wateringCtx.fillStyle = '#34495e';
  wateringCtx.font = '18px sans-serif';
  wateringCtx.textAlign = 'left';

  plants.forEach((plant, index) => {
    const columnIndex = Math.floor(index / maxItemsPerColumn);
    const itemIndexInColumn = index % maxItemsPerColumn;

    const x = leftMargin + columnIndex * columnWidth;
    const y = startY + itemIndexInColumn * itemHeight;

    // Checkbox zeichnen
    wateringCtx.strokeStyle = '#000';
    wateringCtx.lineWidth = 2;
    wateringCtx.strokeRect(x, y - checkboxSize / 2, checkboxSize, checkboxSize);

    // Checkbox Hintergrund
    wateringCtx.fillStyle = '#ffffff';
    wateringCtx.fillRect(x + 1, y - checkboxSize / 2 + 1, checkboxSize - 2, checkboxSize - 2);

    // Pflanzenname
    wateringCtx.fillStyle = '#000';
    wateringCtx.fillText(plant.name, x + checkboxSize + 15, y + 5);
  });
};

export const WateringPlanCanvas: React.FC<WateringPlanCanvasProps> = ({
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
    drawWateringPlan(ctx, plants);
  }, [plants, width, height]);

  return <canvas ref={canvasRef} width={width} height={height} />;
};
