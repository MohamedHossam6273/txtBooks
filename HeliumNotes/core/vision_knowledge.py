"""
vision_knowledge.py
Implements the Vision Board and Knowledge Graph logic.
"""

from data.database import get_connection
import networkx as nx


class VisionKnowledge:
    """Manages relationships and visualization data."""

    @staticmethod
    def create_relation(from_id: int, to_id: int, relation_type: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO relations (from_id, to_id, relation_type)
            VALUES (?, ?, ?)
        """, (from_id, to_id, relation_type))
        conn.commit()
        conn.close()

    @staticmethod
    def get_relations():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM relations")
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def build_graph():
        """Build a NetworkX graph for visualization."""
        conn = get_connection()
        cursor = conn.cursor()
        G = nx.Graph()

        cursor.execute("SELECT id, title FROM notes")
        for row in cursor.fetchall():
            G.add_node(f"Note {row['id']}", type="note", label=row["title"])

        cursor.execute("SELECT id, objectives FROM plans")
        for row in cursor.fetchall():
            G.add_node(f"Plan {row['id']}", type="plan", label=row["objectives"][:20])

        cursor.execute("SELECT id, task FROM tasks")
        for row in cursor.fetchall():
            G.add_node(f"Task {row['id']}", type="task", label=row["task"][:20])

        cursor.execute("SELECT from_id, to_id, relation_type FROM relations")
        for rel in cursor.fetchall():
            G.add_edge(f"Note {rel['from_id']}", f"Plan {rel['to_id']}", label=rel["relation_type"])

        conn.close()
        return G