import numpy as np
from interface import EmbeddingModel as EmbeddingModelInterface
from interface import VectorStorage as VectorStorageInterface

class SearchSystem():
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SearchSystem, cls).__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        vector_storage: VectorStorageInterface = None,
        textual_embedding_model: EmbeddingModelInterface = None,
        visual_embedding_model: EmbeddingModelInterface = None
    ):
        if not hasattr(self, '_initialized'):
            self.textual_embedding_model = textual_embedding_model
            self.visual_embedding_model = visual_embedding_model
            self.vector_storage = vector_storage
            self._initialized = True

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of SearchSystem"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def insert_record(self, record: dict):
        """Insert a record into the vector storage"""
        
        textual_embedding = self.embed_text(record['caption'])
        visual_embedding = self.embed_image(record['image_path'])

        try:
            self.vector_storage.insert(textual_embedding, visual_embedding, record)
        except Exception as e:
            print(f"Error inserting record: {e}")

    def embed_image(self, image_path: str) -> np.ndarray:
        return self.visual_embedding_model.embed_image(image_path)
    
    def embed_text(self, text: str) -> np.ndarray:
        return self.textual_embedding_model.embed_text(text)

    def image_search(self, image_path: str, top_k: int = 10) -> list[dict]:
        try:
            query_visual_embedding = self.embed_image(image_path)
            recommendations = self.vector_storage.search(
                query_visual_embedding, top_k, 'visual'
            )

            return recommendations
        except Exception as e:
            print(f"Error recommending products: {e}")

        return []

    def text_search(self, query: str, top_k: int = 10) -> list[dict]:
        try:
            query_textual_embedding = self.embed_text(query)
            recommendations = self.vector_storage.search(
                query_textual_embedding, top_k, 'textual'
            )

            return recommendations

        except Exception as e:
            print(f"Error recommending products: {e}")

        return []
