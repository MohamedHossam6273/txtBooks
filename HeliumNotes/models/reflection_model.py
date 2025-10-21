from data.database import get_connection
from datetime import datetime


class ReflectionModel:
    """Stores and retrieves weekly reflection summaries."""

    @staticmethod
    def create(week_start, completed_tasks, ongoing_plans, issues, summary):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO reflections (week_start, completed_tasks, ongoing_plans, issues, summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (week_start, completed_tasks, ongoing_plans, issues, summary, now))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reflections ORDER BY created_at DESC")
        reflections = cursor.fetchall()
        conn.close()
        return reflections