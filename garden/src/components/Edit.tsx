import React, { useState, useEffect } from 'react';
import { useGardenData } from '../hooks/useGardenData';
import { GardenApiService } from '../services/gardenApi';
import type { PlantConfig, ArealConfig, GardenData } from '../types/garden';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';
import './Edit.scss';

interface ApiPlant {
  id: number;
  name: string;
  health: string;
  image_path: string;
  size: string;
  position: string;
  areal_id: string;
}

interface EditablePlant extends PlantConfig {
  id?: number;
  areal_id?: string;
}

interface EditableAreal extends ArealConfig {
  plants: EditablePlant[];
}

interface SaveMessage {
  type: 'success' | 'error';
  message: string;
}

const Edit: React.FC = () => {
  const { gardenConfig, loading, error } = useGardenData();
  const [saveMessage, setSaveMessage] = useState<SaveMessage | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [editData, setEditData] = useState<EditableAreal[]>([]);
  const [allPlants, setAllPlants] = useState<ApiPlant[]>([]);

  // Fetch all plants with their IDs from the API
  useEffect(() => {
    const fetchPlantsWithIds = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/garden/plants');
        if (response.ok) {
          const plants = await response.json();
          setAllPlants(plants);
        }
      } catch (err) {
        console.error('Error fetching plants with IDs:', err);
      }
    };

    fetchPlantsWithIds();
  }, []);

  // Initialize edit data when garden data loads
  useEffect(() => {
    if (gardenConfig?.areals && allPlants.length > 0) {
      // Convert garden data to editable format with real IDs from API
      const editableAreals: EditableAreal[] = gardenConfig.areals.map(areal => {
        // Find plants for this areal from the API data
        const arealPlants = allPlants
          .filter(plant => plant.areal_id === areal.id)
          .map(plant => ({
            id: plant.id,
            name: plant.name,
            health: plant.health as "healthy" | "okay" | "dead",
            imagePath: plant.image_path || '',
            size: plant.size as "small" | "medium" | "big",
            position: plant.position || '',
            areal_id: plant.areal_id
          }));

        return {
          ...areal,
          plants: arealPlants
        };
      });
      setEditData(editableAreals);
    }
  }, [gardenConfig, allPlants]);

  const refetchData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/garden/plants');
      if (response.ok) {
        const plants = await response.json();
        setAllPlants(plants);

        // Also update editData to reflect the new plants
        if (gardenConfig?.areals) {
          const editableAreals: EditableAreal[] = gardenConfig.areals.map(areal => {
            const arealPlants = plants
              .filter((plant: ApiPlant) => plant.areal_id === areal.id)
              .map((plant: ApiPlant) => ({
                id: plant.id,
                name: plant.name,
                health: plant.health as "healthy" | "okay" | "dead",
                imagePath: plant.image_path || '',
                size: plant.size as "small" | "medium" | "big",
                position: plant.position || '',
                areal_id: plant.areal_id
              }));

            return {
              ...areal,
              plants: arealPlants
            };
          });
          setEditData(editableAreals);
        }
      }
    } catch (err) {
      console.error('Error refetching data:', err);
    }
  };

  const showSaveMessage = (type: 'success' | 'error', message: string) => {
    setSaveMessage({ type, message });
    setTimeout(() => setSaveMessage(null), 5000);
  };

  const handlePlantChange = (arealIndex: number, plantIndex: number, field: keyof EditablePlant, value: string | number) => {
    setEditData(prev => {
      const newData = [...prev];
      newData[arealIndex].plants[plantIndex] = {
        ...newData[arealIndex].plants[plantIndex],
        [field]: value
      };
      return newData;
    });
  };

  const handleArealChange = (arealIndex: number, field: keyof EditableAreal, value: string | number) => {
    setEditData(prev => {
      const newData = [...prev];
      newData[arealIndex] = {
        ...newData[arealIndex],
        [field]: value
      };
      return newData;
    });
  };

  const addPlant = (event: React.MouseEvent, arealIndex: number) => {
    event.preventDefault();
    event.stopPropagation();

    setEditData(prev => {
      const areal = prev[arealIndex];
      const newPlant: EditablePlant = {
        name: `New Plant ${areal.plants.length + 1}`,
        health: 'healthy',
        imagePath: '',
        size: 'small',
        position: '',
        areal_id: areal.id,
        id: undefined // Will be assigned by backend
      };

      const newData = [...prev];
      newData[arealIndex] = {
        ...areal,
        plants: [...areal.plants, newPlant]
      };
      return newData;
    });
  };

  const removePlant = async (arealIndex: number, plantIndex: number) => {
    const plant = editData[arealIndex].plants[plantIndex];

    // If plant has an ID, delete it from backend
    if (plant.id) {
      setIsSaving(true);
      try {
        const result = await GardenApiService.deletePlant(plant.id);
        if (result.success) {
          showSaveMessage('success', result.message || 'Plant deleted successfully');
          await refetchData(); // Refresh data
          // Update allPlants state
          setAllPlants(prev => prev.filter(p => p.id !== plant.id));
        } else {
          showSaveMessage('error', result.error || 'Failed to delete plant');
          setIsSaving(false);
          return;
        }
      } catch (err) {
        showSaveMessage('error', 'Failed to delete plant');
        setIsSaving(false);
        return;
      }
      setIsSaving(false);
    }

    // Remove from local state
    setEditData(prev => {
      const newData = [...prev];
      newData[arealIndex].plants.splice(plantIndex, 1);
      return newData;
    });
  };

  const addAreal = () => {
    setEditData(prev => {
      const newAreal: EditableAreal = {
        id: `areal_${Date.now()}`,
        name: `New Area ${prev.length + 1}`,
        horizontalPos: 'left',
        verticalPos: 'top',
        size: 'medium',
        plants: []
      };

      return [...prev, newAreal];
    });
  };

  const removeAreal = async (arealIndex: number) => {
    const areal = editData[arealIndex];

    setIsSaving(true);
    try {
      const result = await GardenApiService.deleteAreal(areal.id);
      if (result.success) {
        showSaveMessage('success', result.message || 'Area deleted successfully');
        await refetchData(); // Refresh data
        // Remove from local state
        setEditData(prev => {
          const newData = [...prev];
          newData.splice(arealIndex, 1);
          return newData;
        });
        // Update allPlants state to remove plants from this areal
        setAllPlants(prev => prev.filter(p => p.areal_id !== areal.id));
      } else {
        showSaveMessage('error', result.error || 'Failed to delete area');
      }
    } catch (err) {
      showSaveMessage('error', 'Failed to delete area');
    }
    setIsSaving(false);
  };

  const saveChanges = async () => {
    setIsSaving(true);

    try {
      const savePromises: Promise<{ success: boolean; message?: string; error?: string }>[] = [];

      // Save all areals and plants
      for (const areal of editData) {
        // Update areal - convert position strings to numbers for API
        const arealUpdates = {
          name: areal.name,
          horizontal_pos: areal.horizontalPos,
          vertical_pos: areal.verticalPos,
          size: areal.size
        };

        // Check if areal exists in original data
        const originalAreal = gardenConfig?.areals.find(a => a.id === areal.id);
        if (originalAreal) {
          // Update existing areal
          savePromises.push(GardenApiService.updateAreal(areal.id, arealUpdates));
        } else {
          // Create new areal
          savePromises.push(GardenApiService.createAreal({
            id: areal.id,
            ...arealUpdates
          }));
        }

        // Save plants
        for (const plant of areal.plants) {
          const plantData = {
            areal_id: areal.id,
            name: plant.name,
            health: plant.health,
            image_path: plant.imagePath,
            size: plant.size,
            position: plant.position
          };

          if (plant.id && plant.id > 0) {
            // Update existing plant
            savePromises.push(GardenApiService.updatePlant(plant.id, {
              name: plant.name,
              health: plant.health,
              image_path: plant.imagePath,
              size: plant.size,
              position: plant.position
            }));
          } else {
            // Create new plant
            savePromises.push(GardenApiService.createPlant(plantData));
          }
        }
      }

      const results = await Promise.all(savePromises);
      const failed = results.filter(r => !r.success);

      if (failed.length === 0) {
        showSaveMessage('success', 'All changes saved successfully!');
        await refetchData(); // Refresh data from backend
      } else {
        showSaveMessage('error', `${failed.length} operations failed. Please check and try again.`);
      }
    } catch (err) {
      showSaveMessage('error', 'Failed to save changes. Please try again.');
    }

    setIsSaving(false);
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!editData.length) return <ErrorMessage message="No garden data available" />;

  return (
    <div className="edit-container">
      <div className="edit-header">
        <h1>Edit Garden</h1>
        <div className="edit-actions">
          <button
            className="add-button"
            onClick={addAreal}
            disabled={isSaving}
          >
            Add Area
          </button>
          <button
            className="save-button"
            onClick={saveChanges}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save All Changes'}
          </button>
        </div>
      </div>

      {saveMessage && (
        <div className={`save-message ${saveMessage.type}`}>
          {saveMessage.message}
        </div>
      )}

      <div className="areals-list">
        {editData.map((areal, arealIndex) => (
          <div key={areal.id} className="areal-editor">
            <div className="areal-header">
              <h2>Area: {areal.name}</h2>
              <button
                className="remove-button small"
                onClick={() => removeAreal(arealIndex)}
                disabled={isSaving}
              >
                Remove Area
              </button>
            </div>

            <div className="areal-properties">
              <div className="property-group">
                <label>Name</label>
                <input
                  type="text"
                  value={areal.name}
                  onChange={(e) => handleArealChange(arealIndex, 'name', e.target.value)}
                />
              </div>
              <div className="property-group">
                <label>Horizontal Position</label>
                <select
                  value={areal.horizontalPos}
                  onChange={(e) => handleArealChange(arealIndex, 'horizontalPos', e.target.value)}
                >
                  <option value="left">Left</option>
                  <option value="right">Right</option>
                </select>
              </div>
              <div className="property-group">
                <label>Vertical Position</label>
                <select
                  value={areal.verticalPos}
                  onChange={(e) => handleArealChange(arealIndex, 'verticalPos', e.target.value)}
                >
                  <option value="top">Top</option>
                  <option value="middle">Middle</option>
                  <option value="bottom">Bottom</option>
                </select>
              </div>
              <div className="property-group">
                <label>Size</label>
                <select
                  value={areal.size}
                  onChange={(e) => handleArealChange(arealIndex, 'size', e.target.value)}
                >
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>
            </div>

            <div className="plants-section">
              <div className="plants-header">
                <h3>Plants ({areal.plants.length})</h3>
                <button
                  className="add-button small"
                  onClick={(e) => addPlant(e, arealIndex)}
                  disabled={isSaving}
                >
                  Add Plant
                </button>
              </div>

              <div className="plants-list">
                {areal.plants.map((plant, plantIndex) => (
                  <div key={`${areal.id}-${plantIndex}`} className="plant-editor">
                    <div className="plant-header">
                      <h4>{plant.name} {plant.id && <span className="plant-id">(ID: {plant.id})</span>}</h4>
                      <button
                        className="remove-button small"
                        onClick={() => removePlant(arealIndex, plantIndex)}
                        disabled={isSaving}
                      >
                        Remove
                      </button>
                    </div>

                    <div className="plant-properties">
                      <div className="property-group">
                        <label>Name</label>
                        <input
                          type="text"
                          value={plant.name}
                          onChange={(e) => handlePlantChange(arealIndex, plantIndex, 'name', e.target.value)}
                        />
                      </div>
                      <div className="property-group">
                        <label>Health</label>
                        <select
                          value={plant.health}
                          onChange={(e) => handlePlantChange(arealIndex, plantIndex, 'health', e.target.value)}
                        >
                          <option value="healthy">Healthy</option>
                          <option value="okay">Okay</option>
                          <option value="dead">Dead</option>
                        </select>
                      </div>
                      <div className="property-group">
                        <label>Size</label>
                        <select
                          value={plant.size}
                          onChange={(e) => handlePlantChange(arealIndex, plantIndex, 'size', e.target.value)}
                        >
                          <option value="small">Small</option>
                          <option value="medium">Medium</option>
                          <option value="big">Big</option>
                        </select>
                      </div>
                      <div className="property-group">
                        <label>Position</label>
                        <select
                          value={plant.position}
                          onChange={(e) => handlePlantChange(arealIndex, plantIndex, 'position', e.target.value)}
                        >
                          <option value="">Select Position</option>
                          <option value="center">Center</option>
                          <option value="top">Top</option>
                          <option value="bottom">Bottom</option>
                          <option value="left">Left</option>
                          <option value="right">Right</option>
                          <option value="top-left">Top Left</option>
                          <option value="top-right">Top Right</option>
                          <option value="bottom-left">Bottom Left</option>
                          <option value="bottom-right">Bottom Right</option>
                          <option value="center-top-mid">Center Top Mid</option>
                        </select>
                      </div>
                      <div className="property-group">
                        <label>Image Path</label>
                        <input
                          type="text"
                          value={plant.imagePath}
                          onChange={(e) => handlePlantChange(arealIndex, plantIndex, 'imagePath', e.target.value)}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="edit-footer">
        <p className="disclaimer">
          Complete editing interface with full CRUD functionality. You can add, edit, and remove plants and areas.
          Changes are automatically synced with the backend database.
        </p>
      </div>
    </div>
  );
};

export default Edit;
