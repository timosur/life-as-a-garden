import { useEffect, useRef, useState } from 'react';

interface Plant {
  x: number;
  y: number;
  name: string;
  src: string;
  health: 'healthy' | 'okay' | 'dead';
  size: 'small' | 'medium' | 'big';
}

interface PlantConfig {
  name: string;
  health: 'healthy' | 'okay' | 'dead';
  imagePath: string;
  size: 'small' | 'medium' | 'big';
  position: string;
}

interface ArealConfig {
  id: string;
  name: string;
  horizontalPos: 'left' | 'right';
  verticalPos: 'top' | 'middle' | 'bottom';
  size: 'small' | 'medium' | 'large';
  plants: PlantConfig[];
}

interface GardenData {
  areals: ArealConfig[];
}

// Utility function to get all unique plant images from garden data
const getUniqueImagePaths = (data: GardenData): string[] => {
  const imagePaths = new Set<string>();
  data.areals.forEach(areal => {
    areal.plants.forEach(plant => {
      imagePaths.add(plant.imagePath);
    });
  });
  return Array.from(imagePaths);
};

// Utility function to preload all images for better performance
const preloadPlantImages = async (data: GardenData): Promise<void> => {
  const uniqueImagePaths = getUniqueImagePaths(data);
  const loadPromises = uniqueImagePaths.map(async (imagePath) => {
    if (!imageCache[imagePath]) {
      const imageSrc = await loadPlantImage(imagePath);
      imageCache[imagePath] = imageSrc;
    }
  });

  await Promise.all(loadPromises);
};

// Dynamic plant image loader
const loadPlantImage = async (imagePath: string): Promise<string> => {
  try {
    const module = await import(`../assets/plants/${imagePath}.png`);
    return module.default;
  } catch (error) {
    console.error(`Failed to load plant image: ${imagePath}`, error);
    // Return a fallback or empty string
    return '';
  }
};

// Cache for loaded images to avoid re-importing
const imageCache: { [key: string]: string } = {};

// Funktion zur Generierung von Pflanzen basierend auf Garden-Daten
const generatePlantsFromData = async (data: GardenData, canvasWidth: number, canvasHeight: number): Promise<Plant[]> => {
  const config = getCanvasConfig(canvasWidth);
  const plants: Plant[] = [];

  for (const areal of data.areals) {
    const arealCoords = getArealCoordinatesWithSize(
      areal.horizontalPos,
      areal.verticalPos,
      config.areal.radius,
      canvasHeight,
      config.path,
      areal.size
    );

    for (const plantConfig of areal.plants) {
      // Load image dynamically with caching
      let imageSrc = imageCache[plantConfig.imagePath];
      if (!imageSrc) {
        imageSrc = await loadPlantImage(plantConfig.imagePath);
        imageCache[plantConfig.imagePath] = imageSrc;
      }

      const plantPosition = getPlantPosition(
        arealCoords.x,
        arealCoords.y,
        arealCoords.radius,
        plantConfig.size,
        plantConfig.position
      );

      const plant: Plant = {
        name: plantConfig.name,
        health: plantConfig.health,
        src: imageSrc,
        x: plantPosition.x,
        y: plantPosition.y,
        size: plantConfig.size
      };

      plants.push(plant);
    }
  }

  return plants;
};

// Funktion zur Berechnung der Canvas-abhängigen Konfiguration
const getCanvasConfig = (canvasWidth: number) => {
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
    case 'center-top-mid':
      result.x = arealXMid;
      result.y = arealYMid - radius * 0.1;
      break;
    default:
      break;
  }

  return result;
}


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

// Funktion zum Zeichnen aller Areale basierend auf Garden-Daten
const drawArealsFromData = (ctx: CanvasRenderingContext2D, data: GardenData, canvasWidth: number, canvasHeight: number, pathConfig: { x: number; width: number }) => {
  data.areals.forEach(areal => {
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

// API-Service für echte REST API
const API_BASE_URL = 'http://localhost:8000';

const GardenApiService = {
  async getGardenData(): Promise<GardenData | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/garden`);
      if (!response.ok) {
        throw new Error('Failed to fetch garden data');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching garden data:', error);
      // Fallback to local data if API is not available
      return null;
    }
  },
};



const CanvasGarden = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wateringPlanRef = useRef<HTMLCanvasElement>(null);
  const [gardenConfig, setGardenConfig] = useState<GardenData | null>(null);
  const [plants, setPlants] = useState<Plant[]>([]);
  const [loading, setLoading] = useState(true);

  // Load garden data and generate plants
  useEffect(() => {
    const fetchGardenData = async () => {
      try {
        setLoading(true);
        const data = await GardenApiService.getGardenData();
        setGardenConfig(data);

        if (!data) {
          throw new Error('No garden data available');
        }

        // Preload all images for better performance
        await preloadPlantImages(data);

        // Generate plants with dynamic image loading
        if (data) {
          const generatedPlants = await generatePlantsFromData(data, 1100, 1400);
          setPlants(generatedPlants);
        }
      } catch (error) {
        console.error('Fehler beim Laden der Gartendaten:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGardenData();
  }, []);

  // Render the canvas when data is ready
  useEffect(() => {
    if (!gardenConfig || loading || plants.length === 0) return;

    // Hauptgarten Canvas
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

    // Gießplan Canvas
    const wateringCanvas = wateringPlanRef.current;
    if (!wateringCanvas) return;

    const wateringCtx = wateringCanvas.getContext('2d');
    if (!wateringCtx) return;

    wateringCtx.clearRect(0, 0, wateringCanvas.width, wateringCanvas.height);
    drawWateringPlan(wateringCtx, plants);
  }, [gardenConfig, loading, plants]);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '400px',
        fontSize: '18px'
      }}>
        Lade Gartendaten...
      </div>
    );
  }

  if (!gardenConfig) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '400px',
        fontSize: '18px',
        color: 'red'
      }}>
        Fehler beim Laden der Gartendaten
      </div>
    );
  }

  return (
    <div>
      <canvas ref={canvasRef} width={1100} height={1400} />

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
