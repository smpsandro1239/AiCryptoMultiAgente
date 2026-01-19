import sqlite3
import json
import os
import numpy as np
from datetime import datetime
from typing import Any, List

class PersistentSemanticMemory:
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    key TEXT,
                    value TEXT
                )
            """)

    def add(self, key: str, value: Any):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO memory (timestamp, key, value) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), key, json.dumps(value))
            )

    def query(self, query_str: str) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT timestamp, key, value FROM memory WHERE value LIKE ?",
                (f"%{query_str}%",)
            )
            return [
                {"timestamp": row[0], "key": row[1], "value": json.loads(row[2])}
                for row in cursor.fetchall()
            ]

class VectorMemory:
    """
    Suporte para armazenamento e pesquisa de embeddings de regime utilizando distância Euclidiana.
    """
    def __init__(self):
        self.embeddings = [] # List of tuples (embedding, metadata)

    def add(self, embedding: List[float], metadata: dict):
        self.embeddings.append((np.array(embedding), metadata))

    def search(self, query_embedding: List[float], top_k: int = 5):
        if not self.embeddings:
            return []

        query_vec = np.array(query_embedding)
        distances = []

        for emb, meta in self.embeddings:
            dist = np.linalg.norm(emb - query_vec) # Distância Euclidiana
            distances.append((dist, meta))

        # Ordenar por distância (menor é melhor)
        distances.sort(key=lambda x: x[0])
        return distances[:top_k]

    def save(self, filepath: str):
        """Guarda os embeddings e metadados em disco."""
        data = {
            "embeddings": [emb.tolist() for emb, _ in self.embeddings],
            "metadata": [meta for _, meta in self.embeddings]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def load(self, filepath: str):
        """Carrega os embeddings e metadados do disco."""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.embeddings = [
                    (np.array(emb), meta)
                    for emb, meta in zip(data["embeddings"], data["metadata"])
                ]
