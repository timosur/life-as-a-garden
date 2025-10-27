import React, { useState, useEffect } from 'react';
import { useGardenData } from '../hooks/useGardenData';
import { GardenApiService } from '../services/gardenApi';
import type { PlantConfig, ArealConfig, Note } from '../types/garden';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';
import './Edit.scss';

interface EditablePlant extends PlantConfig {
  id?: number;
  areal_id?: string;
  last_watered?: string;
  days_without_water?: number;
  water_streak?: number;
  total_water_count?: number;
}

interface PlantWithWateringData extends PlantConfig {
  id?: number;
  last_watered?: string;
  days_without_water?: number;
  water_streak?: number;
  total_water_count?: number;
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
  const [originalData, setOriginalData] = useState<EditableAreal[]>([]);

  // Notes state
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedNoteId, setSelectedNoteId] = useState<number | null>(null);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [noteContent, setNoteContent] = useState<string>('');
  const [notesLoading, setNotesLoading] = useState(false);
  const [isCreatingNewNote, setIsCreatingNewNote] = useState(false);
  const [newNoteDate, setNewNoteDate] = useState<string>('');

  // Initialize edit data when garden data loads
  useEffect(() => {
    if (gardenConfig?.areals) {
      // Convert garden data to editable format - plants already include IDs from /garden endpoint
      const editableAreals: EditableAreal[] = gardenConfig.areals.map(areal => {
        // Convert plants to editable format - plants from /garden should have IDs
        const arealPlants: EditablePlant[] = areal.plants.map((plant, index) => {
          const plantWithWateringData = plant as PlantWithWateringData;
          return {
            // Type assertion since we know /garden endpoint includes IDs
            id: plantWithWateringData.id || -(index + 1), // Use negative IDs for new plants
            name: plant.name,
            health: plant.health as "healthy" | "okay" | "dead",
            imagePath: plant.imagePath || '',
            size: plant.size as "small" | "medium" | "big",
            position: plant.position || '',
            areal_id: areal.id,
            last_watered: plantWithWateringData.last_watered || '', // Keep as empty string for HTML date input
            days_without_water: plantWithWateringData.days_without_water || 0,
            water_streak: plantWithWateringData.water_streak || 0,
            total_water_count: plantWithWateringData.total_water_count || 0,
          };
        });

        return {
          ...areal,
          plants: arealPlants
        };
      });
      setEditData(editableAreals);
      // Store original data for comparison
      setOriginalData(JSON.parse(JSON.stringify(editableAreals))); // Deep copy
    }
  }, [gardenConfig]);

  // Fetch all notes on component mount
  useEffect(() => {
    const fetchNotes = async () => {
      setNotesLoading(true);
      try {
        const response = await GardenApiService.getAllNotes();
        if (response?.success && response.notes) {
          setNotes(response.notes);
        }
      } catch (err) {
        console.error('Error fetching notes:', err);
      }
      setNotesLoading(false);
    };

    fetchNotes();
  }, []);

  // Handle note selection
  useEffect(() => {
    if (selectedNoteId && notes.length > 0) {
      const note = notes.find(n => n.id === selectedNoteId);
      if (note) {
        setSelectedNote(note);
        setNoteContent(note.content);
      }
    } else {
      setSelectedNote(null);
      setNoteContent('');
    }
  }, [selectedNoteId, notes]);

  const refetchData = async () => {
    try {
      const data = await GardenApiService.getGardenData();
      if (data?.areals) {
        // Update editData with fresh data from backend
        const editableAreals: EditableAreal[] = data.areals.map(areal => {
          const arealPlants: EditablePlant[] = areal.plants.map((plant, index) => {
            const plantWithWateringData = plant as PlantWithWateringData;
            return {
              // Plants from /garden endpoint should have IDs, but handle missing ones
              id: plantWithWateringData.id || -(index + 1),
              name: plant.name,
              health: plant.health as "healthy" | "okay" | "dead",
              imagePath: plant.imagePath || '',
              size: plant.size as "small" | "medium" | "big",
              position: plant.position || '',
              areal_id: areal.id,
              last_watered: plantWithWateringData.last_watered || '', // Keep as empty string for HTML date input
              days_without_water: plantWithWateringData.days_without_water || 0,
              water_streak: plantWithWateringData.water_streak || 0,
              total_water_count: plantWithWateringData.total_water_count || 0,
            };
          });

          return {
            ...areal,
            plants: arealPlants
          };
        });
        setEditData(editableAreals);
        // Update original data after successful refetch
        setOriginalData(JSON.parse(JSON.stringify(editableAreals))); // Deep copy
      }
    } catch (err) {
      console.error('Error refetching data:', err);
    }
  };

  const saveNote = async () => {
    if (!selectedNote) return;

    setIsSaving(true);
    try {
      const result = await GardenApiService.updateNote(selectedNote.id, noteContent);
      if (result.success) {
        showSaveMessage('success', 'Note saved successfully!');

        // Update the note in local state
        setNotes(prev => prev.map(note =>
          note.id === selectedNote.id
            ? { ...note, content: noteContent, updated_at: new Date().toISOString() }
            : note
        ));

        // Update selectedNote as well
        setSelectedNote(prev => prev
          ? { ...prev, content: noteContent, updated_at: new Date().toISOString() }
          : null
        );
      } else {
        showSaveMessage('error', result.error || 'Failed to save note');
      }
    } catch (err) {
      console.error('Error saving note:', err);
      showSaveMessage('error', 'Failed to save note. Please try again.');
    }
    setIsSaving(false);
  };

  const deleteNote = async () => {
    if (!selectedNote) return;

    // Confirm deletion
    if (!window.confirm(`Are you sure you want to delete the note from ${selectedNote.extracted_at}? This action cannot be undone.`)) {
      return;
    }

    setIsSaving(true);
    try {
      const result = await GardenApiService.deleteNote(selectedNote.id);
      if (result.success) {
        showSaveMessage('success', 'Note deleted successfully!');

        // Remove the note from local state
        setNotes(prev => prev.filter(note => note.id !== selectedNote.id));

        // Clear selected note
        setSelectedNote(null);
        setSelectedNoteId(null);
        setNoteContent('');
      } else {
        showSaveMessage('error', result.error || 'Failed to delete note');
      }
    } catch (err) {
      console.error('Error deleting note:', err);
      showSaveMessage('error', 'Failed to delete note. Please try again.');
    }
    setIsSaving(false);
  };

  const createNote = async () => {
    if (!newNoteDate.trim() || !noteContent.trim()) {
      showSaveMessage('error', 'Please provide both date and content for the new note');
      return;
    }

    setIsSaving(true);
    try {
      const result = await GardenApiService.createNote({
        extracted_at: newNoteDate,
        content: noteContent
      });

      if (result.success && result.note) {
        showSaveMessage('success', 'Note created successfully!');

        // Add the new note to local state
        const newNote = result.note;
        setNotes(prev => [...prev, newNote].sort((a, b) =>
          new Date(b.extracted_at).getTime() - new Date(a.extracted_at).getTime()
        ));

        // Select the new note
        setSelectedNoteId(newNote.id);
        setSelectedNote(newNote);

        // Exit creation mode
        setIsCreatingNewNote(false);
        setNewNoteDate('');
      } else {
        showSaveMessage('error', result.error || 'Failed to create note');
      }
    } catch (err) {
      console.error('Error creating note:', err);
      showSaveMessage('error', 'Failed to create note. Please try again.');
    }
    setIsSaving(false);
  };

  const startCreateNote = () => {
    setIsCreatingNewNote(true);
    setSelectedNote(null);
    setSelectedNoteId(null);
    setNoteContent('');
    setNewNoteDate(new Date().toISOString().split('T')[0]); // Today's date as default
  };

  const cancelCreateNote = () => {
    setIsCreatingNewNote(false);
    setNewNoteDate('');
    setNoteContent('');
  };

  const showSaveMessage = (type: 'success' | 'error', message: string) => {
    setSaveMessage({ type, message });
    setTimeout(() => setSaveMessage(null), 5000);
  };

  // Helper function to compare areal objects (excluding plants)
  const areAreasEqual = (areal1: EditableAreal, areal2: EditableAreal) => {
    return areal1.name === areal2.name &&
      areal1.horizontalPos === areal2.horizontalPos &&
      areal1.verticalPos === areal2.verticalPos &&
      areal1.size === areal2.size;
  };

  // Helper function to compare plant objects
  const arePlantsEqual = (plant1: EditablePlant, plant2: EditablePlant) => {
    return plant1.name === plant2.name &&
      plant1.health === plant2.health &&
      plant1.imagePath === plant2.imagePath &&
      plant1.size === plant2.size &&
      plant1.position === plant2.position &&
      plant1.last_watered === plant2.last_watered &&
      plant1.days_without_water === plant2.days_without_water &&
      plant1.water_streak === plant2.water_streak &&
      plant1.total_water_count === plant2.total_water_count &&
      plant1.areal_id === plant2.areal_id;
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
        id: undefined, // Will be assigned by backend
        last_watered: '',
        days_without_water: 0,
        water_streak: 0,
        total_water_count: 0,
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
        } else {
          showSaveMessage('error', result.error || 'Failed to delete plant');
          setIsSaving(false);
          return;
        }
      } catch (err) {
        console.error('Error deleting plant:', err);
        showSaveMessage('error', 'Failed to delete plant');
        setIsSaving(false);
        return;
      }
      setIsSaving(false);
    }
  };

  const movePlant = async (plantId: number, newArealId: string, currentArealIndex: number) => {
    if (!plantId || newArealId === editData[currentArealIndex].id) {
      return; // No move needed if same area
    }

    setIsSaving(true);
    try {
      const result = await GardenApiService.movePlant(plantId, newArealId);
      if (result.success) {
        showSaveMessage('success', result.message || 'Plant moved successfully');
        await refetchData(); // Refresh data to reflect the move
      } else {
        showSaveMessage('error', result.error || 'Failed to move plant');
      }
    } catch (err) {
      console.error('Error moving plant:', err);
      showSaveMessage('error', 'Failed to move plant');
    }
    setIsSaving(false);
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
      } else {
        showSaveMessage('error', result.error || 'Failed to delete area');
      }
    } catch (err) {
      console.error('Error deleting area:', err);
      showSaveMessage('error', 'Failed to delete area');
    }
    setIsSaving(false);
  };

  const saveChanges = async () => {
    setIsSaving(true);

    try {
      const savePromises: Promise<{ success: boolean; message?: string; error?: string }>[] = [];
      let changesCount = 0;

      // Process each current areal
      for (const currentAreal of editData) {
        const originalAreal = originalData.find(a => a.id === currentAreal.id);

        if (originalAreal) {
          // Check if areal properties have changed
          if (!areAreasEqual(currentAreal, originalAreal)) {
            const arealUpdates = {
              name: currentAreal.name,
              horizontal_pos: currentAreal.horizontalPos,
              vertical_pos: currentAreal.verticalPos,
              size: currentAreal.size
            };
            savePromises.push(GardenApiService.updateAreal(currentAreal.id, arealUpdates));
            changesCount++;
          }
        } else {
          // New areal - always save
          const arealUpdates = {
            name: currentAreal.name,
            horizontal_pos: currentAreal.horizontalPos,
            vertical_pos: currentAreal.verticalPos,
            size: currentAreal.size
          };
          savePromises.push(GardenApiService.createAreal({
            id: currentAreal.id,
            ...arealUpdates
          }));
          changesCount++;
        }

        // Process plants in this areal
        for (const currentPlant of currentAreal.plants) {
          let originalPlant: EditablePlant | undefined;

          // Find original plant by ID across all areals
          if (currentPlant.id && currentPlant.id > 0) {
            for (const origAreal of originalData) {
              originalPlant = origAreal.plants.find(p => p.id === currentPlant.id);
              if (originalPlant) break;
            }
          }

          const plantData = {
            areal_id: currentAreal.id,
            name: currentPlant.name,
            health: currentPlant.health,
            image_path: currentPlant.imagePath,
            size: currentPlant.size,
            position: currentPlant.position,
            last_watered: currentPlant.last_watered || undefined,
            days_without_water: currentPlant.days_without_water || 0,
            water_streak: currentPlant.water_streak || 0,
            total_water_count: currentPlant.total_water_count || 0,
          };

          if (originalPlant) {
            // Check if plant has changed
            if (!arePlantsEqual(currentPlant, originalPlant)) {
              savePromises.push(GardenApiService.updatePlant(currentPlant.id!, {
                name: currentPlant.name,
                health: currentPlant.health,
                image_path: currentPlant.imagePath,
                size: currentPlant.size,
                position: currentPlant.position,
                last_watered: currentPlant.last_watered || undefined,
                days_without_water: currentPlant.days_without_water,
                water_streak: currentPlant.water_streak,
                total_water_count: currentPlant.total_water_count,
              }));
              changesCount++;
            }
          } else {
            // New plant - always save
            savePromises.push(GardenApiService.createPlant(plantData));
            changesCount++;
          }
        }
      }

      // Check for deleted areals (exist in original but not in current)
      for (const originalAreal of originalData) {
        const currentAreal = editData.find(a => a.id === originalAreal.id);
        if (!currentAreal) {
          // Areal was deleted - this should have been handled by removeAreal function
          // but we can add it here for completeness
          console.log(`Areal ${originalAreal.id} was deleted`);
        }
      }

      if (changesCount === 0) {
        showSaveMessage('success', 'No changes to save.');
        setIsSaving(false);
        return;
      }

      const results = await Promise.all(savePromises);
      const failed = results.filter(r => !r.success);

      if (failed.length === 0) {
        showSaveMessage('success', `${changesCount} changes saved successfully!`);
        await refetchData(); // Refresh data from backend
      } else {
        showSaveMessage('error', `${failed.length} of ${changesCount} operations failed. Please check and try again.`);
      }
    } catch (err) {
      console.error('Error saving changes:', err);
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
                      <div className="plant-actions">
                        {plant.id && (
                          <div className="move-plant-section">
                            <label>Move to Area:</label>
                            <select
                              onChange={(e) => {
                                if (e.target.value && plant.id) {
                                  movePlant(plant.id, e.target.value, arealIndex);
                                  e.target.value = ''; // Reset selection
                                }
                              }}
                              disabled={isSaving}
                              defaultValue=""
                            >
                              <option value="">Select area...</option>
                              {editData
                                .filter(a => a.id !== areal.id) // Exclude current area
                                .map(a => (
                                  <option key={a.id} value={a.id}>
                                    {a.name}
                                  </option>
                                ))
                              }
                            </select>
                          </div>
                        )}
                        <button
                          className="remove-button small"
                          onClick={() => removePlant(arealIndex, plantIndex)}
                          disabled={isSaving}
                        >
                          Remove
                        </button>
                      </div>
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
                      <div className="property-group">
                        <label>Last Watered</label>
                        <input
                          type="date"
                          value={plant.last_watered || ''}
                          onChange={(e) => handlePlantChange(arealIndex, plantIndex, 'last_watered', e.target.value)}
                        />
                      </div>
                      <div className="property-group">
                        <label>Days Without Water</label>
                        <input
                          type="number"
                          min="0"
                          value={plant.days_without_water || 0}
                          onChange={(e) => handlePlantChange(arealIndex, plantIndex, 'days_without_water', parseInt(e.target.value) || 0)}
                        />
                      </div>
                      <div className="property-group">
                        <label>Water Streak</label>
                        <input
                          type="number"
                          min="0"
                          value={plant.water_streak || 0}
                          onChange={(e) => handlePlantChange(arealIndex, plantIndex, 'water_streak', parseInt(e.target.value) || 0)}
                        />
                      </div>
                      <div className="property-group">
                        <label>Total Water Count</label>
                        <input
                          type="number"
                          min="0"
                          value={plant.total_water_count || 0}
                          onChange={(e) => handlePlantChange(arealIndex, plantIndex, 'total_water_count', parseInt(e.target.value) || 0)}
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
          Plants can be moved between areas and include detailed watering statistics and growth tracking.
          Notes can be edited and deleted as needed. All changes are automatically synced with the backend database.
        </p>
      </div>

      {/* Notes Editing Section */}
      <div className="notes-editing-section">
        <div className="notes-header">
          <h2>Edit Notes</h2>
          <div className="notes-actions">
            {!isCreatingNewNote && (
              <button
                className="add-button"
                onClick={startCreateNote}
                disabled={isSaving}
              >
                Create New Note
              </button>
            )}
            {isCreatingNewNote && (
              <>
                <button
                  className="save-button"
                  onClick={createNote}
                  disabled={isSaving || !noteContent.trim() || !newNoteDate.trim()}
                >
                  {isSaving ? 'Creating...' : 'Create Note'}
                </button>
                <button
                  className="cancel-button"
                  onClick={cancelCreateNote}
                  disabled={isSaving}
                >
                  Cancel
                </button>
              </>
            )}
            {selectedNote && !isCreatingNewNote && (
              <>
                <button
                  className="save-button"
                  onClick={saveNote}
                  disabled={isSaving || !noteContent.trim()}
                >
                  {isSaving ? 'Saving...' : 'Save Note'}
                </button>
                <button
                  className="remove-button"
                  onClick={deleteNote}
                  disabled={isSaving}
                >
                  {isSaving ? 'Deleting...' : 'Delete Note'}
                </button>
              </>
            )}
          </div>
        </div>

        <div className="notes-controls">
          {isCreatingNewNote ? (
            <div className="property-group">
              <label>Date for New Note</label>
              <input
                type="date"
                value={newNoteDate}
                onChange={(e) => setNewNoteDate(e.target.value)}
                disabled={isSaving}
              />
            </div>
          ) : (
            <div className="property-group">
              <label>Select Note by Date</label>
              <select
                value={selectedNoteId || ''}
                onChange={(e) => setSelectedNoteId(e.target.value ? Number(e.target.value) : null)}
                disabled={notesLoading}
              >
                <option value="">Select a note...</option>
                {notes.map((note) => (
                  <option key={note.id} value={note.id}>
                    {note.extracted_at} (ID: {note.id})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {notesLoading && (
          <div className="notes-loading">
            <LoadingSpinner />
            <p>Loading notes...</p>
          </div>
        )}

        {selectedNote && !isCreatingNewNote && (
          <div className="note-editor">
            <div className="note-info">
              <p><strong>Date:</strong> {selectedNote.extracted_at}</p>
              <p><strong>Created:</strong> {new Date(selectedNote.created_at).toLocaleString()}</p>
              <p><strong>Updated:</strong> {new Date(selectedNote.updated_at).toLocaleString()}</p>
            </div>

            <div className="note-content-editor">
              <label>Note Content</label>
              <textarea
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                disabled={isSaving}
                rows={15}
                placeholder="Enter note content..."
              />
              <p className="character-count">{noteContent.length} characters</p>
            </div>
          </div>
        )}

        {isCreatingNewNote && (
          <div className="note-editor">
            <div className="note-info">
              <p><strong>Creating new note for:</strong> {newNoteDate || 'Select a date'}</p>
            </div>

            <div className="note-content-editor">
              <label>Note Content</label>
              <textarea
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                disabled={isSaving}
                rows={15}
                placeholder="Enter content for the new note..."
              />
              <p className="character-count">{noteContent.length} characters</p>
            </div>
          </div>
        )}

        {!notesLoading && notes.length === 0 && (
          <div className="no-notes">
            <p>No notes found. Notes will appear here once they are created in the system.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Edit;
