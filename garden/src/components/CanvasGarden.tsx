import { GardenCanvas } from './GardenCanvas';
import { WateringPlanCanvas } from './WateringPlanCanvas';
import { PlantStatusChanges } from './PlantStatusChanges';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';
import { useGardenData } from '../hooks/useGardenData';
import './PDFLayout.scss';

const CanvasGarden = () => {
  const { gardenConfig, plants, loading, error } = useGardenData(1100, 1400);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error || !gardenConfig) {
    return <ErrorMessage message={error || undefined} />;
  }

  return (
    <div className="pdf-layout">
      {/* Page 1: Garden Overview */}
      <div className="pdf-page page-garden">
        <GardenCanvas
          gardenConfig={gardenConfig}
          plants={plants}
          width={1100}
          height={1400}
        />
      </div>

      {/* Page 2: Watering Plan/Checklist */}
      <div className="pdf-page page-checklist">
        <WateringPlanCanvas
          plants={plants}
          width={1100}
          height={1400}
        />
      </div>

      {/* Page 3: Site to comment on checked water items */}
      <div className="pdf-page page-comment">
        {/* Placeholder for comment section */}
      </div>

      {/* Page 4: Status Changes */}
      <div className="pdf-page page-status-changes">
        <PlantStatusChanges />
      </div>
    </div>
  );
};

export default CanvasGarden;
