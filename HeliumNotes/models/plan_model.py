from data.database import get_connection
from datetime import datetime


class PlanModel:
    """Handles CRUD operations for AI-generated business plans."""

    @staticmethod
    def create(note_id: int, objectives: str, tasks: str):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO plans (note_id, objectives, tasks, created_at)
            VALUES (?, ?, ?, ?)
        """, (note_id, objectives, tasks, now))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_note(note_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM plans WHERE note_id=?", (note_id,))
        plan = cursor.fetchone()
        conn.close()
        return plan

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM plans ORDER BY created_at DESC")
        plans = cursor.fetchall()
        conn.close()
        return plans