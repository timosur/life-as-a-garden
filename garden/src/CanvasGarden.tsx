import React, { useEffect, useRef } from 'react';
import happyBamboo from './assets/plants/happy-bamboo.png';
import rose from './assets/plants/rose.png';
import sunflower from './assets/plants/sunflower.png';
import cactus from './assets/plants/cactus.png';
import lavendel from './assets/plants/lavendel.png';
import thymian from './assets/plants/thymian.png';
import lotusFlower from './assets/plants/lotus-flower.png';
import oatGrass from './assets/plants/oat-grass.png';
import waterHyacinth from './assets/plants/water-hyacinth.png'
import hop from './assets/plants/hop.png'
import grass from './assets/plants/grass.png'

interface Plant {
  x: number;
  y: number;
  name: string;
  src: string;
  health: 'healthy' | 'okay' | 'dead';
  size: 'small' | 'medium' | 'big';
}

// Funktion zur Berechnung der Canvas-abhängigen Konfiguration
const getCanvasConfig = (canvasWidth: number, canvasHeight: number) => {
  const arealRadius = canvasWidth * 0.18; // 12.5% der Canvas-Breite
  const pathWidth = canvasWidth * 0.025; // 2.5% der Canvas-Breite
  const pathX = (canvasWidth - pathWidth) / 2;

  // Areale-Positionen basierend auf Canvas-Größe
  const familyX = canvasWidth * 0.266;
  const sportX = canvasWidth * 0.734;
  const arealY = canvasHeight * 0.75;

  return {
    areal: {
      radius: arealRadius,
      family: { x: familyX, y: arealY },
      sport: { x: sportX, y: arealY }
    },
    path: {
      width: pathWidth,
      x: pathX
    }
  };
};

const getPlantPosition = (arealX: number, arealY: number, radius: number, plantSizeStr: Plant['size'], position: string): { x: number; y: number, size: Plant['size'] } => {
  const plantSize = getPlantSize(plantSizeStr);
  const arealXMid = arealX - plantSize / 2;
  const arealYMid = arealY - plantSize / 2;

  const result = { x: arealXMid, y: arealYMid, size: plantSizeStr };

  switch (position) {
    case 'top':
      result.x = arealXMid;
      result.y = arealYMid - radius * 0.6;
      break;
    case 'bottom':
      result.x = arealXMid;
      result.y = arealYMid + radius * 0.6;
      break;
    case 'left':
      result.x = arealX - radius * 0.8;
      result.y = arealYMid;
      break;
    case 'right':
      result.x = arealX + radius * 0.4;
      result.y = arealYMid;
      break;
    case 'top-left':
      result.x = arealX - radius * 0.6;
      result.y = arealYMid - radius * 0.6;
      break;
    case 'top-right':
      result.x = arealX + radius * 0.6;
      result.y = arealYMid - radius * 0.6;
      break;
    case 'bottom-left':
      result.x = arealX - radius * 0.4;
      result.y = arealYMid + radius * 0.6;
      break;
    case 'bottom-right':
      result.x = arealXMid + radius * 0.4;
      result.y = arealYMid + radius * 0.6;
      break;
    case 'center':
      result.x = arealXMid;
      result.y = arealYMid;
      break;
    default:
      break;
  }

  return result;
}


// Funktion zur Berechnung der Pflanzen-Positionen basierend auf Canvas-Größe
const getPlantsForCanvas = (canvasWidth: number, canvasHeight: number): Plant[] => {
  const config = getCanvasConfig(canvasWidth, canvasHeight);

  return [
    // Core Familie - Positionen relativ zum Family-Areal
    {
      name: 'Bobo',
      health: 'healthy',
      src: rose,
      ...getPlantPosition(config.areal.family.x, config.areal.family.y, config.areal.radius, 'big', 'top')
    },
    {
      name: 'Finja',
      health: 'healthy',
      src: sunflower,
      ...getPlantPosition(config.areal.family.x, config.areal.family.y, config.areal.radius, 'big', 'left')
    },
    {
      name: 'Mats',
      health: 'healthy',
      src: happyBamboo,
      ...getPlantPosition(config.areal.family.x, config.areal.family.y, config.areal.radius, 'big', 'right')
    },
    {
      name: 'Mama',
      health: 'healthy',
      src: lavendel,
      ...getPlantPosition(config.areal.family.x, config.areal.family.y, config.areal.radius, 'medium', 'center')
    },
    {
      name: 'Papa',
      health: 'okay',
      src: cactus,
      ...getPlantPosition(config.areal.family.x, config.areal.family.y, config.areal.radius, 'small', 'bottom')
    },

    // sport Areal - Positionen relativ zum sport-Areal
    {
      name: 'Fahrrad fahren',
      health: 'healthy',
      src: thymian,
      ...getPlantPosition(config.areal.sport.x, config.areal.sport.y, config.areal.radius, 'big', 'top')
    },
    {
      name: 'Joggen',
      health: 'okay',
      src: oatGrass,
      ...getPlantPosition(config.areal.sport.x, config.areal.sport.y, config.areal.radius, 'big', 'center')
    },
    {
      name: 'Klettern',
      health: 'healthy',
      src: hop,
      ...getPlantPosition(config.areal.sport.x, config.areal.sport.y, config.areal.radius, 'big', 'left')
    },
    {
      name: 'Yoga',
      health: 'healthy',
      src: lotusFlower,
      ...getPlantPosition(config.areal.sport.x, config.areal.sport.y, config.areal.radius, 'medium', 'right')
    },
    {
      name: 'Schwimmen',
      health: 'okay',
      src: waterHyacinth,
      ...getPlantPosition(config.areal.sport.x, config.areal.sport.y, config.areal.radius, 'medium', 'bottom-left')
    },
    {
      name: 'Fußball',
      health: 'dead',
      src: grass,
      ...getPlantPosition(config.areal.sport.x, config.areal.sport.y, config.areal.radius, 'small', 'bottom-right')
    },
  ];
};

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

    // Canvas-basierte Konfiguration berechnen
    const canvasConfig = getCanvasConfig(canvas.width, canvas.height);
    const plants = getPlantsForCanvas(canvas.width, canvas.height);

    // Schotterweg von unten nach oben (mittig)
    const { path } = canvasConfig;

    // Weg-Grundfarbe (heller Grau)
    ctx.fillStyle = '#D3D3D3';
    ctx.fillRect(path.x, 0, path.width, canvas.height);

    // Verbindungswege zu den Arealen
    const connectionWidth = canvas.width * 0.04; // 4% der Canvas-Breite
    const connectionHeight = canvas.height * 0.025; // 2.5% der Canvas-Höhe
    const connectionY = canvasConfig.areal.family.y - connectionHeight / 2;

    // Weg zu Family (links)
    ctx.fillRect(path.x - connectionWidth, connectionY, connectionWidth, connectionHeight);

    // Weg zu sport (rechts) 
    ctx.fillRect(path.x + path.width, connectionY, connectionWidth, connectionHeight);

    // Gartenareale zeichnen (rund, rechts und links vom Weg)
    ctx.fillStyle = '#d0f0c0';

    // Family - links
    ctx.beginPath();
    ctx.arc(canvasConfig.areal.family.x, canvasConfig.areal.family.y, canvasConfig.areal.radius, 0, 2 * Math.PI);
    ctx.fill();

    // sport - rechts
    ctx.beginPath();
    ctx.arc(canvasConfig.areal.sport.x, canvasConfig.areal.sport.y, canvasConfig.areal.radius, 0, 2 * Math.PI);
    ctx.fill();

    // Areal-Beschriftungen
    ctx.fillStyle = '#000';
    ctx.font = `${canvas.width * 0.02}px sans-serif`; // 2% der Canvas-Breite
    ctx.textAlign = 'center';
    const labelOffset = canvasConfig.areal.radius + 30;
    ctx.fillText('Core Family', canvasConfig.areal.family.x, canvasConfig.areal.family.y + labelOffset);
    ctx.fillText('Sport', canvasConfig.areal.sport.x, canvasConfig.areal.sport.y + labelOffset);

    // Draw garden areas with borders (runde Ränder)
    ctx.strokeStyle = '#8B4513';
    ctx.lineWidth = 3;

    // Family border
    ctx.beginPath();
    ctx.arc(canvasConfig.areal.family.x, canvasConfig.areal.family.y, canvasConfig.areal.radius, 0, 2 * Math.PI);
    ctx.stroke();

    // sport border
    ctx.beginPath();
    ctx.arc(canvasConfig.areal.sport.x, canvasConfig.areal.sport.y, canvasConfig.areal.radius, 0, 2 * Math.PI);
    ctx.stroke();

    // Weg-Ränder
    ctx.strokeStyle = '#8B4513';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(path.x, 0);
    ctx.lineTo(path.x, canvas.height);
    ctx.moveTo(path.x + path.width, 0);
    ctx.lineTo(path.x + path.width, canvas.height);
    ctx.stroke();

    // Ränder für Verbindungswege
    // Family Weg Ränder
    ctx.beginPath();
    ctx.moveTo(path.x - connectionWidth, connectionY);
    ctx.lineTo(path.x, connectionY);
    ctx.moveTo(path.x - connectionWidth, connectionY + connectionHeight);
    ctx.lineTo(path.x, connectionY + connectionHeight);
    ctx.stroke();

    // sport Weg Ränder
    ctx.beginPath();
    ctx.moveTo(path.x + path.width, connectionY);
    ctx.lineTo(path.x + path.width + connectionWidth, connectionY);
    ctx.moveTo(path.x + path.width, connectionY + connectionHeight);
    ctx.lineTo(path.x + path.width + connectionWidth, connectionY + connectionHeight);
    ctx.stroke();

    // Eingangstor am unteren Ende
    const gateWidth = canvas.width * 0.025; // 2.5% der Canvas-Breite
    const gateHeight = canvas.height * 0.0375; // 3.75% der Canvas-Höhe
    ctx.fillStyle = '#8B4513';
    ctx.fillRect(path.x - gateWidth / 2, canvas.height - gateHeight, gateWidth, gateHeight);
    ctx.fillRect(path.x + path.width - gateWidth / 2, canvas.height - gateHeight, gateWidth, gateHeight);

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

    drawWateringPlan(wateringCtx, plants);
  }, []);

  return (
    <div>
      <canvas ref={canvasRef} width={1200} height={1200} />

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
