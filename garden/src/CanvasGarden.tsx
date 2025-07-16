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
import bonsai from './assets/plants/bonsai.png'
import ivy from './assets/plants/ivy.png'
import sage from './assets/plants/sage.png'
import sequoia from './assets/plants/sequoia.png'
import aloeVera from './assets/plants/aloe-vera.png'
import snowdrop from './assets/plants/snowdrop.png'
import marigold from './assets/plants/marigold.png'
import cucumber from './assets/plants/cucumber.png'
import blackLotus from './assets/plants/black-lotus.png'
import cypress from './assets/plants/cypress.png'
import dandelion from './assets/plants/dandelion.png'
import oak from './assets/plants/oak.png'

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
  const arealRadius = canvasWidth * 0.18; // 18% der Canvas-Breite
  const pathWidth = canvasWidth * 0.025; // 2.5% der Canvas-Breite
  const pathX = (canvasWidth - pathWidth) / 2;

  // Areale-Positionen basierend auf Canvas-Größe
  const familyX = canvasWidth * 0.266;
  const sportX = canvasWidth * 0.734;
  const arealY = canvasHeight * 0.75;

  // Weg-Positionen
  const pathPositions = {
    bottom: {
      left: { x: pathX - arealRadius * 0.8, y: canvasHeight * 0.85 },
      right: { x: pathX + pathWidth + arealRadius * 0.8, y: canvasHeight * 0.85 }
    },
    middle: {
      left: { x: pathX - arealRadius * 0.8, y: canvasHeight * 0.5 },
      right: { x: pathX + pathWidth + arealRadius * 0.8, y: canvasHeight * 0.5 }
    },
    top: {
      left: { x: pathX - arealRadius * 0.8, y: canvasHeight * 0.15 },
      right: { x: pathX + pathWidth + arealRadius * 0.8, y: canvasHeight * 0.15 }
    }
  };

  return {
    areal: {
      radius: arealRadius,
      family: { x: familyX, y: arealY },
      sport: { x: sportX, y: arealY }
    },
    path: {
      width: pathWidth,
      x: pathX,
      positions: pathPositions
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

  // Koordinaten der Areale berechnen (mit verschiedenen Größen)
  const familyCoords = getArealCoordinatesWithSize('left', 'bottom', config.areal.radius, canvasHeight, config.path, 'large');
  const sportCoords = getArealCoordinatesWithSize('right', 'bottom', config.areal.radius, canvasHeight, config.path, 'large');
  const mentalHealthCoords = getArealCoordinatesWithSize('left', 'middle', config.areal.radius, canvasHeight, config.path, 'large');
  const hobbiesCoords = getArealCoordinatesWithSize('right', 'top', config.areal.radius, canvasHeight, config.path, 'small');
  const workCoords = getArealCoordinatesWithSize('left', 'top', config.areal.radius, canvasHeight, config.path, 'small');
  const extendedFamilyCoords = getArealCoordinatesWithSize('right', 'middle', config.areal.radius, canvasHeight, config.path, 'medium');

  return [
    // Core Familie - Positionen relativ zum Family-Areal
    {
      name: 'Bobo',
      health: 'healthy',
      src: rose,
      ...getPlantPosition(familyCoords.x, familyCoords.y, familyCoords.radius, 'big', 'top')
    },
    {
      name: 'Finja',
      health: 'healthy',
      src: sunflower,
      ...getPlantPosition(familyCoords.x, familyCoords.y, familyCoords.radius, 'big', 'left')
    },
    {
      name: 'Mats',
      health: 'healthy',
      src: happyBamboo,
      ...getPlantPosition(familyCoords.x, familyCoords.y, familyCoords.radius, 'big', 'right')
    },
    {
      name: 'Mama',
      health: 'healthy',
      src: lavendel,
      ...getPlantPosition(familyCoords.x, familyCoords.y, familyCoords.radius, 'medium', 'center')
    },
    {
      name: 'Papa',
      health: 'okay',
      src: cactus,
      ...getPlantPosition(familyCoords.x, familyCoords.y, familyCoords.radius, 'small', 'bottom')
    },

    // sport Areal - Positionen relativ zum sport-Areal
    {
      name: 'Fahrrad fahren',
      health: 'healthy',
      src: thymian,
      ...getPlantPosition(sportCoords.x, sportCoords.y, sportCoords.radius, 'big', 'top')
    },
    {
      name: 'Joggen',
      health: 'okay',
      src: oatGrass,
      ...getPlantPosition(sportCoords.x, sportCoords.y, sportCoords.radius, 'big', 'center')
    },
    {
      name: 'Klettern',
      health: 'healthy',
      src: hop,
      ...getPlantPosition(sportCoords.x, sportCoords.y, sportCoords.radius, 'big', 'left')
    },
    {
      name: 'Yoga',
      health: 'healthy',
      src: lotusFlower,
      ...getPlantPosition(sportCoords.x, sportCoords.y, sportCoords.radius, 'medium', 'right')
    },
    {
      name: 'Schwimmen',
      health: 'okay',
      src: waterHyacinth,
      ...getPlantPosition(sportCoords.x, sportCoords.y, sportCoords.radius, 'medium', 'bottom-left')
    },
    {
      name: 'Fußball',
      health: 'dead',
      src: grass,
      ...getPlantPosition(sportCoords.x, sportCoords.y, sportCoords.radius, 'small', 'bottom-right')
    },

    // Mental Health Areal - Positionen relativ zum Mental Health-Areal (medium size)
    {
      name: 'Meditation',
      health: 'healthy',
      src: bonsai,
      ...getPlantPosition(mentalHealthCoords.x, mentalHealthCoords.y, mentalHealthCoords.radius, 'big', 'center')
    },
    {
      name: 'Lesen',
      health: 'healthy',
      src: ivy,
      ...getPlantPosition(mentalHealthCoords.x, mentalHealthCoords.y, mentalHealthCoords.radius, 'medium', 'left')
    },
    {
      name: 'Journaling',
      health: 'healthy',
      src: sage,
      ...getPlantPosition(mentalHealthCoords.x, mentalHealthCoords.y, mentalHealthCoords.radius, 'medium', 'right')
    },
    {
      name: 'Waldbaden',
      health: 'okay',
      src: sequoia,
      ...getPlantPosition(mentalHealthCoords.x, mentalHealthCoords.y, mentalHealthCoords.radius, 'medium', 'bottom')
    },
    {
      name: 'Psychotherapie',
      health: 'healthy',
      src: aloeVera,
      ...getPlantPosition(mentalHealthCoords.x, mentalHealthCoords.y, mentalHealthCoords.radius, 'big', 'top')
    },

    // Extended Family Area
    {
      name: 'Oma',
      health: 'dead',
      src: snowdrop,
      ...getPlantPosition(extendedFamilyCoords.x, extendedFamilyCoords.y, extendedFamilyCoords.radius, 'small', 'center')
    },
    {
      name: 'Frankes',
      health: 'healthy',
      src: marigold,
      ...getPlantPosition(extendedFamilyCoords.x, extendedFamilyCoords.y, extendedFamilyCoords.radius, 'big', 'left')
    },
    {
      name: 'Schwiegereltern',
      health: 'healthy',
      src: cucumber,
      ...getPlantPosition(extendedFamilyCoords.x, extendedFamilyCoords.y, extendedFamilyCoords.radius, 'big', 'right')
    },

    // Hobbies Area
    {
      name: 'Magic',
      health: 'dead',
      src: blackLotus,
      ...getPlantPosition(hobbiesCoords.x, hobbiesCoords.y, hobbiesCoords.radius, 'small', 'bottom')
    },
    {
      name: 'Schach',
      health: 'okay',
      src: cypress,
      ...getPlantPosition(hobbiesCoords.x, hobbiesCoords.y, hobbiesCoords.radius, 'medium', 'center')
    },

    // Work Area
    {
      name: 'Spaß bei der Arbeit',
      health: 'okay',
      src: dandelion,
      ...getPlantPosition(workCoords.x, workCoords.y, workCoords.radius, 'medium', 'center')
    },
    {
      name: 'Sinn in der Arbeit',
      health: 'dead',
      src: oak,
      ...getPlantPosition(workCoords.x, workCoords.y, workCoords.radius, 'small', 'bottom')
    }
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

// Funktion zum Zeichnen eines Areals mit automatischem Verbindungsweg
const drawAreal = (ctx: CanvasRenderingContext2D, horizontalPos: 'left' | 'right', verticalPos: 'top' | 'middle' | 'bottom', baseRadius: number, label: string, canvasWidth: number, canvasHeight: number, pathConfig: { x: number; width: number }, size: 'small' | 'medium' | 'large' = 'large') => {
  // Tatsächliche Radius basierend auf Size berechnen
  const radius = getArealSize(size, baseRadius);

  // Koordinaten basierend auf Position berechnen
  const { x, y } = getArealCoordinates(horizontalPos, verticalPos, radius, canvasHeight, pathConfig);

  // Areal zeichnen (rund)
  ctx.fillStyle = '#d0f0c0';
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.fill();

  // Areal-Rand zeichnen
  ctx.strokeStyle = '#8B4513';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.stroke();

  // Areal-Beschriftung
  ctx.fillStyle = '#000';
  ctx.font = `${canvasWidth * 0.02}px sans-serif`; // 2% der Canvas-Breite
  ctx.textAlign = 'center';
  const labelOffset = radius + 30;
  ctx.fillText(label, x, y + labelOffset);

  // Verbindungsweg zum Hauptweg zeichnen
  const connectionWidth = pathConfig.width * 1.6;
  const connectionHeight = canvasHeight * 0.025;
  const connectionY = y - connectionHeight / 2;

  ctx.fillStyle = '#D3D3D3';

  if (horizontalPos === 'left') {
    // Weg von links zum Hauptweg
    ctx.fillRect(pathConfig.x - connectionWidth, connectionY, connectionWidth, connectionHeight);

    // Ränder für Verbindungsweg
    ctx.strokeStyle = '#8B4513';
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
    ctx.strokeStyle = '#8B4513';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(pathConfig.x + pathConfig.width, connectionY);
    ctx.lineTo(pathConfig.x + pathConfig.width + connectionWidth, connectionY);
    ctx.moveTo(pathConfig.x + pathConfig.width, connectionY + connectionHeight);
    ctx.lineTo(pathConfig.x + pathConfig.width + connectionWidth, connectionY + connectionHeight);
    ctx.stroke();
  }
};

// Funktion zum Zeichnen des Hauptweges
const drawPath = (ctx: CanvasRenderingContext2D, pathConfig: { x: number; width: number }, canvasHeight: number) => {
  // Hauptweg zeichnen
  ctx.fillStyle = '#D3D3D3';
  ctx.fillRect(pathConfig.x, 0, pathConfig.width, canvasHeight);

  // Weg-Ränder
  ctx.strokeStyle = '#8B4513';
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
  ctx.fillStyle = '#8B4513';
  ctx.fillRect(pathConfig.x - gateWidth / 2, canvasHeight - gateHeight, gateWidth, gateHeight);
  ctx.fillRect(pathConfig.x + pathConfig.width - gateWidth / 2, canvasHeight - gateHeight, gateWidth, gateHeight);
};

// Funktion zur Berechnung der Areal-Koordinaten basierend auf Position
const getArealCoordinates = (horizontalPos: 'left' | 'right', verticalPos: 'top' | 'middle' | 'bottom', radius: number, canvasHeight: number, pathConfig: { x: number; width: number }) => {
  let x: number, y: number;

  // X-Koordinate berechnen - dynamischer Abstand basierend auf Radius
  const minDistance = radius + pathConfig.width * 1.65; // Mindestabstand = Radius + halbe Pfadbreite

  if (horizontalPos === 'left') {
    x = pathConfig.x - minDistance; // Links vom Weg
  } else {
    x = pathConfig.x + pathConfig.width + minDistance; // Rechts vom Weg
  }

  // Y-Koordinate berechnen
  switch (verticalPos) {
    case 'top':
      y = canvasHeight * 0.15;
      break;
    case 'middle':
      y = canvasHeight * 0.45;
      break;
    case 'bottom':
      y = canvasHeight * 0.81;
      break;
  }

  return { x, y };
};

// Funktion zur Berechnung der Areal-Größe basierend auf Size-Parameter
const getArealSize = (size: 'small' | 'medium' | 'large', baseRadius: number) => {
  switch (size) {
    case 'small':
      return baseRadius * 0.6; // 60% der Basis-Größe
    case 'medium':
      return baseRadius * 0.8; // 80% der Basis-Größe
    case 'large':
      return baseRadius; // 100% der Basis-Größe (Standard)
    default:
      return baseRadius;
  }
};

// Hilfsfunktion zur Berechnung der Areal-Koordinaten mit Size für Pflanzen-Positionierung
const getArealCoordinatesWithSize = (horizontalPos: 'left' | 'right', verticalPos: 'top' | 'middle' | 'bottom', baseRadius: number, canvasHeight: number, pathConfig: { x: number; width: number }, size: 'small' | 'medium' | 'large' = 'large') => {
  const radius = getArealSize(size, baseRadius);
  return {
    ...getArealCoordinates(horizontalPos, verticalPos, radius, canvasHeight, pathConfig),
    radius
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

    // Hauptweg zeichnen
    drawPath(ctx, canvasConfig.path, canvas.height);

    // Areale mit Verbindungswegen zeichnen
    drawAreal(ctx, 'left', 'bottom', canvasConfig.areal.radius, 'Core Family', canvas.width, canvas.height, canvasConfig.path, 'large');
    drawAreal(ctx, 'right', 'bottom', canvasConfig.areal.radius, 'Sport', canvas.width, canvas.height, canvasConfig.path, 'large');
    drawAreal(ctx, 'left', 'middle', canvasConfig.areal.radius, 'Mental Health', canvas.width, canvas.height, canvasConfig.path, 'large');
    drawAreal(ctx, 'right', 'middle', canvasConfig.areal.radius, 'Extended Family', canvas.width, canvas.height, canvasConfig.path, 'medium');
    drawAreal(ctx, 'right', 'top', canvasConfig.areal.radius, 'Hobbies', canvas.width, canvas.height, canvasConfig.path, 'small');
    drawAreal(ctx, 'left', 'top', canvasConfig.areal.radius, 'Work', canvas.width, canvas.height, canvasConfig.path, 'small');

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
      <canvas ref={canvasRef} width={1200} height={1400} />

      <div style={{ marginTop: '30px' }}>
        <canvas
          ref={wateringPlanRef}
          width={1000}
          height={800}
        />
      </div>
    </div>
  );
};

export default CanvasGarden;
