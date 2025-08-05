"""Notes service for handling note operations."""

from typing import List, Dict, Any, Optional
from datetime import date
from ..base import DatabaseConnection
from ..repositories.notes import NotesRepository


class NotesService:
    """Service for managing notes data."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize with database connection and repositories."""
        self.db = db_connection
        self.notes_repo = NotesRepository(db_connection)

    def create_note(self, content: str, extracted_at: date) -> int:
        """Create a new note entry."""
        return self.notes_repo.create_note(content, extracted_at)

    def get_notes_by_date(self, date_filter: date) -> List[Dict[str, Any]]:
        """Get all notes for a specific date."""
        return self.notes_repo.get_notes_by_date(date_filter)

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Get all notes ordered by extraction date."""
        return self.notes_repo.get_all_notes()

    def get_notes_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Get notes within a date range."""
        return self.notes_repo.get_notes_by_date_range(start_date, end_date)

    def note_exists_for_date(self, date_filter: date) -> bool:
        """Check if a note exists for a specific date."""
        return self.notes_repo.note_exists_for_date(date_filter)

    def get_latest_note(self) -> Optional[Dict[str, Any]]:
        """Get the most recently extracted note."""
        return self.notes_repo.get_latest_note()

    def update_note(self, note_id: int, content: str) -> bool:
        """Update an existing note's content."""
        return self.notes_repo.update_note(note_id, content)

    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID."""
        return self.notes_repo.delete_note(note_id)
