import React, { useEffect, useState } from 'react';
import { GardenApiService } from '../services/gardenApi';
import type { WateringCalendarEntry } from '../types/garden';
import './Calendar.scss';

interface CalendarProps {
  className?: string;
}

interface CalendarDay {
  date: Date;
  watered_plants: string[];
  isCurrentMonth: boolean;
  isToday: boolean;
}

export const Calendar: React.FC<CalendarProps> = ({ className }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [wateringData, setWateringData] = useState<WateringCalendarEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWateringData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Calculate the first and last day of the month to show in calendar
        const startOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
        const endOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

        // Adjust start date to include previous month days for a complete calendar week
        const startOfCalendar = new Date(startOfMonth);
        startOfCalendar.setDate(startOfCalendar.getDate() - startOfCalendar.getDay());

        // Adjust end date to include next month days for a complete calendar week
        const endOfCalendar = new Date(endOfMonth);
        endOfCalendar.setDate(endOfCalendar.getDate() + (6 - endOfCalendar.getDay()));

        const startDateStr = startOfCalendar.toISOString().split('T')[0];
        const endDateStr = endOfCalendar.toISOString().split('T')[0];

        const response = await GardenApiService.getWateringCalendar(startDateStr, endDateStr);

        if (response.success) {
          setWateringData(response.watering_history || []);
        } else {
          setError(response.error || 'Failed to load watering calendar');
          setWateringData([]);
        }
      } catch (err) {
        setError('Error loading watering calendar');
        setWateringData([]);
        console.error('Calendar fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWateringData();
  }, [currentDate]);

  // Generate calendar days
  const generateCalendarDays = (): CalendarDay[] => {
    // Calculate the first and last day of the month to show in calendar
    const startOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const endOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

    // Adjust start date to include previous month days for a complete calendar week
    const startOfCalendar = new Date(startOfMonth);
    startOfCalendar.setDate(startOfCalendar.getDate() - startOfCalendar.getDay());

    // Adjust end date to include next month days for a complete calendar week
    const endOfCalendar = new Date(endOfMonth);
    endOfCalendar.setDate(endOfCalendar.getDate() + (6 - endOfCalendar.getDay()));

    // Create a map of date -> plants watered for quick lookup
    const wateringMap = new Map<string, string[]>();
    wateringData.forEach(entry => {
      // Adjust display date: watering_date - 1 day (as per user requirement)
      const wateringDate = new Date(entry.watering_date);
      wateringDate.setDate(wateringDate.getDate() - 1);
      const displayDateStr = wateringDate.toISOString().split('T')[0];

      if (!wateringMap.has(displayDateStr)) {
        wateringMap.set(displayDateStr, []);
      }
      wateringMap.get(displayDateStr)!.push(entry.plant_name);
    });

    const days: CalendarDay[] = [];
    const current = new Date(startOfCalendar);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    while (current <= endOfCalendar) {
      const dateStr = current.toISOString().split('T')[0];
      const isCurrentMonth = current.getMonth() === currentDate.getMonth();
      const isToday = current.getTime() === today.getTime();

      days.push({
        date: new Date(current),
        watered_plants: wateringMap.get(dateStr) || [],
        isCurrentMonth,
        isToday
      });

      current.setDate(current.getDate() + 1);
    }

    return days;
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(newDate.getMonth() - 1);
      } else {
        newDate.setMonth(newDate.getMonth() + 1);
      }
      return newDate;
    });
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const formatMonth = (date: Date): string => {
    return date.toLocaleDateString('de-DE', { month: 'long', year: 'numeric' });
  };

  const weekdays = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];
  const calendarDays = generateCalendarDays();

  if (loading) {
    return (
      <div className={`calendar loading ${className || ''}`}>
        <h2>🗓️ Gießkalender</h2>
        <div className="loading-message">
          <h3>🔄 Lädt Gießdaten...</h3>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`calendar error ${className || ''}`}>
        <h2>🗓️ Gießkalender</h2>
        <div className="error-message">
          <h3>⚠️ {error}</h3>
        </div>
      </div>
    );
  }

  return (
    <div className={`calendar ${className || ''}`}>
      <div className="calendar-header">
        <h2>🗓️ Gießkalender</h2>
        <p className="calendar-description">
          Zeigt, welche Pflanzen an welchen Tagen gegossen wurden (Tag der Anzeige = Gießtag - 1)
        </p>

        <div className="calendar-navigation">
          <button
            className="nav-button prev"
            onClick={() => navigateMonth('prev')}
            title="Vorheriger Monat"
          >
            ←
          </button>

          <div className="current-month">
            <h3>{formatMonth(currentDate)}</h3>
          </div>

          <button
            className="nav-button next"
            onClick={() => navigateMonth('next')}
            title="Nächster Monat"
          >
            →
          </button>

          <button
            className="nav-button today"
            onClick={goToToday}
            title="Zu heute springen"
          >
            Heute
          </button>
        </div>
      </div>

      <div className="calendar-grid">
        <div className="weekday-headers">
          {weekdays.map(day => (
            <div key={day} className="weekday-header">
              {day}
            </div>
          ))}
        </div>

        <div className="calendar-days">
          {calendarDays.map((day, index) => (
            <div
              key={index}
              className={`calendar-day ${day.isCurrentMonth ? 'current-month' : 'other-month'} ${day.isToday ? 'today' : ''} ${day.watered_plants.length > 0 ? 'has-watering' : ''}`}
            >
              <div className="day-number">
                {day.date.getDate()}
              </div>

              {day.watered_plants.length > 0 && (
                <div className="watering-info">
                  <div className="watering-count">
                    🚰 {day.watered_plants.length}
                  </div>
                  <div className="plant-list">
                    {day.watered_plants.map((plant, plantIndex) => (
                      <div key={plantIndex} className="plant-name">
                        🌱 {plant}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="calendar-legend">
        <div className="legend-item">
          <div className="legend-color today-legend"></div>
          <span>Heute</span>
        </div>
        <div className="legend-item">
          <div className="legend-color watered-legend"></div>
          <span>Pflanzen gegossen</span>
        </div>
        <div className="legend-item">
          <span className="legend-symbol">🚰</span>
          <span>Anzahl gegossener Pflanzen</span>
        </div>
      </div>
    </div>
  );
};