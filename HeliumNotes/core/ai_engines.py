"""
ai_engines.py
Provides access to small local or API-based AI models like Phi-3-mini.
"""

import os
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np


class AIEngines:
    """Central class for embedding and reasoning models."""

    _embedding_model = None

    @staticmethod
    def get_embedding_model():
        """Load and cache the small embedding model."""
        if AIEngines._embedding_model is None:
            AIEngines._embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return AIEngines._embedding_model

    @staticmethod
    def embed_text(text: str) -> np.ndarray:
        """Compute embedding vector for given text."""
        model = AIEngines.get_embedding_model()
        return np.array(model.encode([text])[0])

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    @staticmethod
    def summarize_text(text: str) -> str:
        """Mock summarizer using simple heuristics (replaceable by Phi-3-mini)."""
        sentences = text.split(".")
        summary = ". ".join(sentences[:3])
        return summary.strip() + "..."

    @staticmethod
    def generate_reflection_report(entries: List[str]) -> str:
        """Simple reflection generator."""
        report = "Weekly Reflection Summary:\n\n"
        for i, e in enumerate(entries, 1):
            report += f"{i}. {e}\n"
        return report