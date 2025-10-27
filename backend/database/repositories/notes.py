"""Notes repository for handwritten text data."""

from typing import List, Dict, Any
from datetime import date
from database.base import DatabaseConnection


class NotesRepository:
    """Repository for managing notes data."""

    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection

    def create_note(self, content: str, extracted_at: date) -> int:
        """Create a new note entry."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO notes (content, extracted_at)
            VALUES (?, ?)
            """,
            (content, extracted_at),
        )

        note_id = cursor.lastrowid
        conn.commit()
        return note_id

    def get_notes_by_date(self, date_filter: date) -> List[Dict[str, Any]]:
        """Get all notes for a specific date."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, content, extracted_at, created_at, updated_at
            FROM notes
            WHERE extracted_at = ?
            ORDER BY created_at DESC
            """,
            (date_filter,),
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Get all notes ordered by extraction date."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, content, extracted_at, created_at, updated_at
            FROM notes
            ORDER BY extracted_at DESC, created_at DESC
            """
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_note_by_id(self, note_id: int) -> Dict[str, Any] | None:
        """Get a single note by ID."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, content, extracted_at, created_at, updated_at
            FROM notes
            WHERE id = ?
            """,
            (note_id,),
        )

        row = cursor.fetchone()
        return dict(row) if row else None

    def get_notes_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Get notes within a date range."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, content, extracted_at, created_at, updated_at
            FROM notes
            WHERE extracted_at BETWEEN ? AND ?
            ORDER BY extracted_at DESC, created_at DESC
            """,
            (start_date, end_date),
        )

        return [dict(row) for row in cursor.fetchall()]

    def update_note(self, note_id: int, content: str) -> bool:
        """Update note content."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE notes 
            SET content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (content, note_id),
        )

        conn.commit()
        return cursor.rowcount > 0

    def delete_note(self, note_id: int) -> bool:
        """Delete a note."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return cursor.rowcount > 0

    def note_exists_for_date(self, date_filter: date) -> bool:
        """Check if a note already exists for a specific date."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM notes WHERE extracted_at = ?", (date_filter,)
        )

        count = cursor.fetchone()[0]
        return count > 0
