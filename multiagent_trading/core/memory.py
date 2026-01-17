import numpy as np

class VectorMemory:
    """
    Simulates a vector database for storing and retrieving regime embeddings.
    """
    def __init__(self):
        self.vectors = [] # List of (embedding_np, metadata_dict)

    def add(self, embedding: list, metadata: dict):
        self.vectors.append((np.array(embedding), metadata))

    def search(self, query_embedding: list, top_k: int = 3):
        """
        Finds the top_k most similar vectors using Euclidean distance.
        """
        if not self.vectors:
            return []

        query = np.array(query_embedding)
        distances = []
        for vec, meta in self.vectors:
            dist = np.linalg.norm(query - vec)
            distances.append((dist, meta))

        # Sort by distance (smaller is better)
        distances.sort(key=lambda x: x[0])
        return distances[:top_k]

    def clear(self):
        self.vectors = []
