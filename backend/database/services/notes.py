"""Notes service for handling note operations."""

from typing import List, Dict, Any, Optional
from datetime import date
from ..repositories.notes import NotesRepository


class NotesService:
    """Service for managing notes data."""

    def __init__(self):
        """Initialize with repositories."""
        self.notes_repo = NotesRepository()

    def create_note(self, content: str, extracted_at: date) -> int:
        return self.notes_repo.create_note(content, extracted_at)

    def get_notes_by_date(self, date_filter: date) -> List[Dict[str, Any]]:
        return self.notes_repo.get_notes_by_date(date_filter)

    def get_all_notes(self) -> List[Dict[str, Any]]:
        return self.notes_repo.get_all_notes()

    def get_note_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        return self.notes_repo.get_note_by_id(note_id)

    def get_notes_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        return self.notes_repo.get_notes_by_date_range(start_date, end_date)

    def note_exists_for_date(self, date_filter: date) -> bool:
        return self.notes_repo.note_exists_for_date(date_filter)

    def get_latest_note(self) -> Optional[Dict[str, Any]]:
        return self.notes_repo.get_latest_note()

    def update_note(self, note_id: int, content: str) -> bool:
        return self.notes_repo.update_note(note_id, content)

    def delete_note(self, note_id: int) -> bool:
        return self.notes_repo.delete_note(note_id)
