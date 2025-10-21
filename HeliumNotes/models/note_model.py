import sqlite3
from data.database import get_connection
from datetime import datetime


class NoteModel:
    """Handles CRUD operations for notes."""

    @staticmethod
    def create(title: str, content: str, tags: str = ""):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO notes (title, content, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (title, content, tags, now, now))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes ORDER BY updated_at DESC")
        notes = cursor.fetchall()
        conn.close()
        return notes

    @staticmethod
    def get(note_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE id=?", (note_id,))
        note = cursor.fetchone()
        conn.close()
        return note

    @staticmethod
    def update(note_id: int, title: str, content: str, tags: str = ""):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE notes SET title=?, content=?, tags=?, updated_at=? WHERE id=?
        """, (title, content, tags, now, note_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(note_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()
        conn.close()