import React, { useEffect, useRef } from 'react';
import happyBamboo from './assets/plants/happy-bamboo.png';
import rose from './assets/plants/rose.png';
import sunflower from './assets/plants/sunflower.png';

interface Plant {
  x: number;
  y: number;
  name: string;
  areal: string;
  src: string;
  health: 'healthy' | 'okay' | 'dead';
  size: 'small' | 'medium' | 'big';
}

const canvasConfig = {
  areal: {
    radius: 150,
  }
}

// Pflanzen-Daten für jedes Areal (angepasst an 800x800 Canvas)
const plants: Plant[] = [
  // Core Familie
  { x: 80, y: 500, name: 'Bobo', areal: 'core-family', health: 'healthy', size: 'big', src: rose },
  { x: 190, y: 500, name: 'Finja', areal: 'core-family', health: 'healthy', size: 'big', src: sunflower },
  { x: 135, y: 390, name: 'Mats', areal: 'core-family', health: 'healthy', size: 'big', src: happyBamboo },

  // Self Areal
  { x: 560, y: 470, name: 'Meditation', areal: 'self', health: 'dead', size: 'small', src: happyBamboo },
  { x: 640, y: 470, name: 'Natur', areal: 'self', health: 'healthy', size: 'medium', src: happyBamboo },
];

// Helper functions for plant visualization
const getPlantSize = (size: Plant['size']) => {
  switch (size) {
    case 'small': return 40;
    case 'medium': return 60;
    case 'big': return 80;
    default: return 60;
  }
};

const getHealthTint = (health: Plant['health']) => {
  switch (health) {
    case 'healthy': return { r: 0, g: 255, b: 0, alpha: 0.2 }; // Green tint
    case 'okay': return { r: 255, g: 255, b: 0, alpha: 0.3 }; // Yellow tint
    case 'dead': return { r: 255, g: 0, b: 0, alpha: 0.4 }; // Red tint
    default: return { r: 0, g: 0, b: 0, alpha: 0 };
  }
};

// Gießplan zeichnen
const drawWateringPlan = (wateringCtx: CanvasRenderingContext2D) => {
  // Pflanzen-Liste
  const startY = 90;
  const itemHeight = 50;
  const checkboxSize = 20;
  const leftMargin = 50;

  wateringCtx.fillStyle = '#34495e';
  wateringCtx.font = '18px sans-serif';
  wateringCtx.textAlign = 'left';

  plants.forEach((plant, index) => {
    const y = startY + index * itemHeight;

    // Checkbox zeichnen
    wateringCtx.strokeStyle = '#000';
    wateringCtx.lineWidth = 2;
    wateringCtx.strokeRect(leftMargin, y - checkboxSize / 2, checkboxSize, checkboxSize);

    // Checkbox Hintergrund
    wateringCtx.fillStyle = '#ffffff';
    wateringCtx.fillRect(leftMargin + 1, y - checkboxSize / 2 + 1, checkboxSize - 2, checkboxSize - 2);

    // Pflanzenname
    wateringCtx.fillStyle = '#000';
    wateringCtx.fillText(plant.name, leftMargin + checkboxSize + 15, y + 5);
  });
};


const drawLegend = (ctx: CanvasRenderingContext2D) => {
  // Add legend for plant health and size
  const legendX = 50;
  const legendY = 50;
  const legendWidth = 200;
  const legendHeight = 120;

  // Legend background
  ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
  ctx.fillRect(legendX, legendY, legendWidth, legendHeight);
  ctx.strokeStyle = '#333';
  ctx.lineWidth = 1;
  ctx.strokeRect(legendX, legendY, legendWidth, legendHeight);

  // Legend title
  ctx.fillStyle = '#333';
  ctx.font = 'bold 16px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('Legende', legendX + 10, legendY + 20);

  // Health indicators
  ctx.font = '12px sans-serif';
  const healthItems = [
    { emoji: '😊', text: 'Gesund' },
    { emoji: '😐', text: 'Okay' },
    { emoji: '😵', text: 'Braucht Hilfe' }
  ];

  healthItems.forEach((item, index) => {
    const y = legendY + 40 + index * 20;

    // Emoji indicator
    ctx.font = '16px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = '#000';
    ctx.fillText(item.emoji, legendX + 15, y + 4);

    // Text
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillStyle = '#333';
    ctx.fillText(item.text, legendX + 30, y + 4);
  });

  // Size info
  ctx.fillText('Größe = Priorität', legendX + 10, legendY + 110);
};

const drawPlantWithEffects = (ctx: CanvasRenderingContext2D, img: string, plant: Plant) => {
  const size = getPlantSize(plant.size);
  const tint = getHealthTint(plant.health);

  const image = new Image();
  image.src = img;

  image.onload = () => {
    // Draw the plant image after it has loaded
    ctx.drawImage(image, plant.x, plant.y, size, size);

    // Apply health tint overlay
    if (tint.alpha > 0) {
      ctx.globalCompositeOperation = 'source-atop';
      ctx.fillStyle = `rgba(${tint.r}, ${tint.g}, ${tint.b}, ${tint.alpha})`;
      ctx.fillRect(plant.x, plant.y, size, size);
      ctx.globalCompositeOperation = 'source-over';
    }

    // Add health indicator (emoji)
    const indicatorX = plant.x + size;
    const indicatorY = plant.y + 15;

    ctx.font = '20px sans-serif';
    ctx.textAlign = 'center';

    let emoji;
    switch (plant.health) {
      case 'healthy':
        emoji = '😊'; // Happy face
        break;
      case 'okay':
        emoji = '😐'; // Neutral face
        break;
      case 'dead':
        emoji = '😵'; // Dizzy/dead face
        break;
    }

    ctx.fillStyle = '#000';
    ctx.fillText(emoji, indicatorX, indicatorY);

    // Plant name (positioned based on plant size)
    ctx.fillStyle = '#000';
    ctx.font = '14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(plant.name, plant.x + size / 2, plant.y - 8);
  };
};

const CanvasGarden = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wateringPlanRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    // Hauptgarten Canvas
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Schotterweg von unten nach oben (mittig, angepasst an 800x800)
    const pathWidth = 30;
    const pathX = (canvas.width - pathWidth) / 2;

    // Weg-Grundfarbe (heller Grau)
    ctx.fillStyle = '#D3D3D3';
    ctx.fillRect(pathX, 0, pathWidth, canvas.height);

    // Verbindungswege zu den Arealen (angepasst an größeres Canvas)
    // Weg zu Family (links unten)
    ctx.fillRect(pathX - 50, 500, 50, 18);

    // Weg zu Work (rechts unten) 
    ctx.fillRect(pathX + pathWidth, 500, 50, 18);

    // Gartenareale zeichnen (rund, rechts und links vom Weg)
    ctx.fillStyle = '#d0f0c0';

    // Family - links unten
    ctx.beginPath();
    ctx.arc(170, 500, canvasConfig.areal.radius, 0, 2 * Math.PI);
    ctx.fill();

    // Work - rechts unten
    ctx.beginPath();
    ctx.arc(630, 500, canvasConfig.areal.radius, 0, 2 * Math.PI);
    ctx.fill();

    // Areal-Beschriftungen
    ctx.fillStyle = '#000';
    ctx.font = '24px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Core Family', 170, 680);
    ctx.fillText('Self', 630, 680);

    // Draw garden areas with borders (runde Ränder)
    ctx.strokeStyle = '#8B4513';
    ctx.lineWidth = 3;

    // Family border
    ctx.beginPath();
    ctx.arc(170, 500, canvasConfig.areal.radius, 0, 2 * Math.PI);
    ctx.stroke();

    // Work border
    ctx.beginPath();
    ctx.arc(630, 500, canvasConfig.areal.radius, 0, 2 * Math.PI);
    ctx.stroke();

    // Weg-Ränder
    ctx.strokeStyle = '#8B4513';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(pathX, 0);
    ctx.lineTo(pathX, canvas.height);
    ctx.moveTo(pathX + pathWidth, 0);
    ctx.lineTo(pathX + pathWidth, canvas.height);
    ctx.stroke();

    // Ränder für Verbindungswege (angepasst an größeres Canvas)
    // Family Weg Ränder
    ctx.beginPath();
    ctx.moveTo(pathX - 50, 500);
    ctx.lineTo(pathX, 500);
    ctx.moveTo(pathX - 50, 518);
    ctx.lineTo(pathX, 518);
    ctx.stroke();

    // Work Weg Ränder
    ctx.beginPath();
    ctx.moveTo(pathX + pathWidth, 500);
    ctx.lineTo(pathX + pathWidth + 50, 500);
    ctx.moveTo(pathX + pathWidth, 518);
    ctx.lineTo(pathX + pathWidth + 50, 518);
    ctx.stroke();

    // Eingangstor am unteren Ende
    ctx.fillStyle = '#8B4513';
    ctx.fillRect(pathX - 15, canvas.height - 30, 30, 30);
    ctx.fillRect(pathX + pathWidth - 15, canvas.height - 30, 30, 30);

    // Place plants in the garden areas
    plants.forEach(plant => {
      drawPlantWithEffects(ctx, plant.src, plant);
    });

    // Draw the legend
    drawLegend(ctx);

    // Gießplan Canvas
    const wateringCanvas = wateringPlanRef.current;
    if (!wateringCanvas) return;

    const wateringCtx = wateringCanvas.getContext('2d');
    if (!wateringCtx) return;

    drawWateringPlan(wateringCtx);
  }, []);

  return (
    <div>
      <canvas ref={canvasRef} width={1200} height={800} />

      <div style={{ marginTop: '30px' }}>
        <canvas
          ref={wateringPlanRef}
          width={800}
          height={800}
        />
      </div>
    </div>
  );
};

export default CanvasGarden;
