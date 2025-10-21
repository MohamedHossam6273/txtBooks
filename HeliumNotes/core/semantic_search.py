"""
semantic_search.py
Handles semantic and AI-powered search through notes using embeddings.
"""

import numpy as np
from core.ai_engines import AIEngines
from data.database import get_connection


class SemanticSearch:
    """Implements embedding storage and semantic retrieval."""

    @staticmethod
    def ensure_table():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                note_id INTEGER,
                vector BLOB
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def index_notes():
        """Generate and store embeddings for all notes."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM notes")
        notes = cursor.fetchall()

        model = AIEngines.get_embedding_model()

        for n in notes:
            text = (n["title"] or "") + " " + (n["content"] or "")
            vector = model.encode([text])[0].astype(np.float32).tobytes()
            cursor.execute("INSERT INTO embeddings (note_id, vector) VALUES (?, ?)", (n["id"], vector))

        conn.commit()
        conn.close()

    @staticmethod
    def search(query: str, top_k: int = 5):
        """Find notes semantically similar to query."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT note_id, vector FROM embeddings")
        rows = cursor.fetchall()
        conn.close()

        query_vec = AIEngines.embed_text(query)
        similarities = []

        for row in rows:
            note_vec = np.frombuffer(row["vector"], dtype=np.float32)
            score = AIEngines.cosine_similarity(query_vec, note_vec)
            similarities.append((row["note_id"], score))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]