"""Notes repository using SQLModel."""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from sqlmodel import select
from ..models import Note
from ..base import get_session


class NotesRepository:
    """Repository for managing notes data."""

    def create_note(self, content: str, extracted_at: date) -> int:
        """Create a new note entry."""
        with get_session() as session:
            note = Note(content=content, extracted_at=extracted_at)
            session.add(note)
            session.commit()
            session.refresh(note)
            return note.id

    def get_notes_by_date(self, date_filter: date) -> List[Dict[str, Any]]:
        """Get all notes for a specific date."""
        with get_session() as session:
            notes = session.exec(
                select(Note)
                .where(Note.extracted_at == date_filter)
                .order_by(Note.created_at.desc())
            ).all()
            return [n.model_dump() for n in notes]

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Get all notes ordered by extraction date."""
        with get_session() as session:
            notes = session.exec(
                select(Note).order_by(Note.extracted_at.desc(), Note.created_at.desc())
            ).all()
            return [n.model_dump() for n in notes]

    def get_note_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Get a single note by ID."""
        with get_session() as session:
            note = session.get(Note, note_id)
            return note.model_dump() if note else None

    def get_notes_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Get notes within a date range."""
        with get_session() as session:
            notes = session.exec(
                select(Note)
                .where(Note.extracted_at >= start_date, Note.extracted_at <= end_date)
                .order_by(Note.extracted_at.desc(), Note.created_at.desc())
            ).all()
            return [n.model_dump() for n in notes]

    def update_note(self, note_id: int, content: str) -> bool:
        """Update note content."""
        with get_session() as session:
            note = session.get(Note, note_id)
            if not note:
                return False
            note.content = content
            note.updated_at = datetime.utcnow()
            session.commit()
            return True

    def delete_note(self, note_id: int) -> bool:
        """Delete a note."""
        with get_session() as session:
            note = session.get(Note, note_id)
            if not note:
                return False
            session.delete(note)
            session.commit()
            return True

    def note_exists_for_date(self, date_filter: date) -> bool:
        """Check if a note already exists for a specific date."""
        with get_session() as session:
            from sqlmodel import func

            count = session.exec(
                select(func.count())
                .select_from(Note)
                .where(Note.extracted_at == date_filter)
            ).one()
            return count > 0

    def get_latest_note(self) -> Optional[Dict[str, Any]]:
        """Get the most recently extracted note."""
        with get_session() as session:
            note = session.exec(
                select(Note)
                .order_by(Note.extracted_at.desc(), Note.created_at.desc())
                .limit(1)
            ).first()
            return note.model_dump() if note else None
