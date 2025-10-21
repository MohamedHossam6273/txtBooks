from data.database import get_connection
from datetime import datetime


class TaskModel:
    """Handles CRUD operations for extracted or user-created tasks."""

    @staticmethod
    def create(note_id: int, task: str, due_date: str = None, person: str = None):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO tasks (note_id, task, due_date, person, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (note_id, task, due_date, person, now))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    @staticmethod
    def update_status(task_id: int, status: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
        conn.commit()
        conn.close()