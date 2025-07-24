import React, { useEffect, useState } from 'react';
import { GardenApiService } from '../services/gardenApi';
import type { PlantStatusChange } from '../types/garden';
import './PlantStatusChanges.scss';

interface PlantStatusChangesProps {
  className?: string;
}

export const PlantStatusChanges: React.FC<PlantStatusChangesProps> = ({ className }) => {
  const [changes, setChanges] = useState<PlantStatusChange[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchChanges = async () => {
      try {
        setLoading(true);
        const response = await GardenApiService.getTodaysChanges();

        if (response && response.success) {
          setChanges(response.status_changes);
          setError(null);
        } else {
          setError('Keine Änderungen gefunden');
          setChanges([]);
        }
      } catch {
        setError('Fehler beim Laden der Statusänderungen');
        setChanges([]);
      } finally {
        setLoading(false);
      }
    };

    fetchChanges();
  }, []);

  const translateHealth = (health: string): string => {
    switch (health) {
      case 'healthy': return 'Gesund';
      case 'okay': return 'Okay';
      case 'dead': return 'Braucht Hilfe';
      default: return health;
    }
  };

  if (loading) {
    return (
      <div className={`plant-status-changes loading ${className || ''}`}>
        <h3>🔄 Lädt Änderungen...</h3>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`plant-status-changes error ${className || ''}`}>
        <h3>⚠️ {error}</h3>
      </div>
    );
  }

  if (changes.length === 0) {
    return (
      <div className={`plant-status-changes empty ${className || ''}`}>
        <div className="empty-state">
          <div className="empty-icon">🌿</div>
          <p>Keine Änderungen heute gefunden.</p>
        </div>
      </div>
    );
  }

  // Calculate summary statistics
  const summary = {
    totalPlants: new Set(changes.map(c => c.plant_name)).size,
    totalChanges: changes.length,
    watered: changes.filter(c => c.change_type === 'watered').length,
    healthImproved: changes.filter(c => {
      const healthOrder = { dead: 0, okay: 1, healthy: 2 };
      return healthOrder[c.new_health as keyof typeof healthOrder] > healthOrder[c.old_health as keyof typeof healthOrder];
    }).length,
    growthIncrease: changes.filter(c => c.new_growth_stage > c.old_growth_stage).length,
  };

  return (
    <div className={`plant-status-changes ${className || ''}`}>
      {/* Compact Summary */}
      <div className="summary-section-compact">
        <div className="summary-line">
          <strong>📊 Zusammenfassung:</strong> {summary.totalPlants} Pflanzen • {summary.watered} gegossen • {summary.healthImproved} verbessert • {summary.growthIncrease} gewachsen
        </div>
      </div>

      <div className="changes-table-container">
        <table className="changes-table">
          <thead>
            <tr>
              <th>Zeit</th>
              <th>Pflanze</th>
              <th>Gesundheit</th>
              <th>Wachstum</th>
              <th>Wasserserie</th>
              <th>Tage ohne Wasser</th>
              <th>Gegossen?</th>
            </tr>
          </thead>
          <tbody>
            {changes
              .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
              .map((change) => (
                <tr key={change.id} className={`change-row ${change.change_type}`}>
                  <td className="time-cell">
                    {new Date(change.created_at).toLocaleTimeString('de-DE', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </td>
                  <td className="plant-cell">{change.plant_name}</td>
                  <td className="health-cell">
                    <div className="stat-change">
                      <span className="stat-values">
                        {translateHealth(change.old_health)} → {translateHealth(change.new_health)}
                      </span>
                      {change.old_health !== change.new_health && (
                        <span className={`change-indicator health-${change.new_health}`}>
                          {change.new_health === 'healthy' ? '😊↗️' :
                            change.new_health === 'okay' ? '�→' : '�↘️'}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="growth-cell">
                    <div className="stat-change">
                      <span className="stat-values">
                        {change.old_growth_stage} → {change.new_growth_stage}
                      </span>
                      {change.new_growth_stage > change.old_growth_stage && (
                        <span className="change-indicator growth-up">
                          📈 +{change.new_growth_stage - change.old_growth_stage}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="water-streak-cell">
                    <div className="stat-change">
                      <span className="stat-values">
                        {change.old_water_streak} → {change.new_water_streak}
                      </span>
                      {change.new_water_streak !== change.old_water_streak && (
                        <span className={`change-indicator ${change.new_water_streak > change.old_water_streak ? 'streak-up' : 'streak-down'}`}>
                          {change.new_water_streak > change.old_water_streak ? '💧↗️' : '💧↘️'}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="days-without-water-cell">
                    <div className="stat-change">
                      <span className="stat-values">
                        {change.old_days_without_water} → {change.new_days_without_water}
                      </span>
                      {change.new_days_without_water === 0 && change.old_days_without_water > 0 && (
                        <span className="change-indicator thirst-quenched">
                          🚰 Durst gestillt
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="watered-cell">
                    <div className="checkbox-container">
                      <span className={`checkbox ${change.change_type === 'watered' ? 'checked' : ''}`}>
                        {change.change_type === 'watered' ? '✅' : '⬜'}
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
