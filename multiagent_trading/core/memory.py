import numpy as np
import sqlite3
import json
import os

class VectorMemory:
    """
    Simula uma base de dados vetorial para armazenar embeddings de regime.
    """
    def __init__(self):
        self.vectors = []

    def add(self, embedding: list, metadata: dict):
        self.vectors.append((np.array(embedding), metadata))

    def search(self, query_embedding: list, top_k: int = 3):
        if not self.vectors:
            return []
        query = np.array(query_embedding)
        distances = []
        for vec, meta in self.vectors:
            dist = np.linalg.norm(query - vec)
            distances.append((dist, meta))
        distances.sort(key=lambda x: x[0])
        return distances[:top_k]

    def clear(self):
        self.vectors = []

class PersistentSemanticMemory:
    """
    Memória semântica com persistência em SQLite.
    """
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def add(self, key: str, value: any):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO semantic_memory (key, value) VALUES (?, ?)',
                       (key, json.dumps(value)))
        conn.commit()
        conn.close()

    def query(self, query_str: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM semantic_memory WHERE value LIKE ?", (f'%{query_str}%',))
        rows = cursor.fetchall()
        conn.close()
        return [{"key": r[0], "value": json.loads(r[1])} for r in rows]

    def get_by_key(self, key: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM semantic_memory WHERE key = ?", (key,))
        rows = cursor.fetchall()
        conn.close()
        return [{"key": r[0], "value": json.loads(r[1])} for r in rows]

    @property
    def memory(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM semantic_memory")
        rows = cursor.fetchall()
        conn.close()
        return [{"key": r[0], "value": json.loads(r[1])} for r in rows]
