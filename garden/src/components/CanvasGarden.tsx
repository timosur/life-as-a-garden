import { GardenCanvas } from './GardenCanvas';
import { WateringPlanCanvas } from './WateringPlanCanvas';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';
import { useGardenData } from '../hooks/useGardenData';

const CanvasGarden = () => {
  const { gardenConfig, plants, loading, error } = useGardenData(1100, 1400);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error || !gardenConfig) {
    return <ErrorMessage message={error || undefined} />;
  }

  return (
    <div>
      <GardenCanvas
        gardenConfig={gardenConfig}
        plants={plants}
        width={1100}
        height={1400}
      />

      <div style={{ marginTop: '30px' }}>
        <WateringPlanCanvas
          plants={plants}
          width={1000}
          height={800}
        />
      </div>
    </div>
  );
};

export default CanvasGarden;
