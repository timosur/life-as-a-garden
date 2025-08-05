import React, { useState, useEffect } from 'react';
import { GardenApiService } from '../services/gardenApi';
import type { Note } from '../types/garden';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';
import './Notes.scss';

const Notes: React.FC = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNotes = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await GardenApiService.getAllNotes();

      if (response && response.success) {
        setNotes(response.notes);
      } else {
        setError(response?.error || 'Failed to fetch notes');
      }
    } catch (err) {
      setError('Failed to fetch notes: ' + String(err));
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Function to render markdown-like content
  const renderMarkdownContent = (content: string) => {
    // Simple markdown rendering for basic formatting
    const lines = content.split('\n');
    return (
      <div className="note-content">
        {lines.map((line, index) => {
          // Handle bullet points
          if (line.trim().startsWith('*') || line.trim().startsWith('-')) {
            return (
              <li key={index} className="bullet-point">
                {line.trim().substring(1).trim()}
              </li>
            );
          }
          // Handle empty lines
          if (line.trim() === '') {
            return <br key={index} />;
          }
          // Regular paragraphs
          return (
            <p key={index} className="paragraph">
              {line}
            </p>
          );
        })}
      </div>
    );
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="notes-container">
      {error && <ErrorMessage message={error} />}

      <div className="notes-list">
        {notes.length === 0 ? (
          <div className="no-notes">
            <p>No notes found.</p>
            <p className="no-notes-subtitle">
              Notes are automatically extracted when you analyze your garden journal.
            </p>
          </div>
        ) : (
          notes.map((note) => (
            <div key={note.id} className="note-card">
              <div className="note-header">
                <h3 className="note-date">{formatDate(note.extracted_at)}</h3>
                <div className="note-meta">
                  <span className="note-timestamp">
                    Added: {formatDateTime(note.created_at)}
                  </span>
                </div>
              </div>
              <div className="note-body">
                {renderMarkdownContent(note.content)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Notes;
