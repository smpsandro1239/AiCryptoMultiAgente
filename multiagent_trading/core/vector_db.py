import numpy as np
from typing import List, Dict

class VectorDBConnector:
    """
    Interface simplificada para uma base de dados vectorial (ex: ChromaDB).
    Suporta armazenamento de documentos e pesquisa por similaridade.
    """
    def __init__(self, collection_name="matf_knowledge"):
        self.collection_name = collection_name
        self.data = [] # Mock de armazenamento: list of {id, vector, document, metadata}

    def add_document(self, doc_id: str, document: str, metadata: dict = None):
        # Simulação de embedding (em produção usaria SentenceTransformers ou OpenAI)
        vector = np.random.randn(128)
        self.data.append({
            "id": doc_id,
            "vector": vector,
            "document": document,
            "metadata": metadata or {}
        })

    def query_similarity(self, query_text: str, top_k=3) -> List[Dict]:
        """Retorna os documentos mais similares."""
        if not self.data:
            return []

        # Simulação de pesquisa vectorial
        results = sorted(self.data, key=lambda x: np.random.random())[:top_k]
        return results
