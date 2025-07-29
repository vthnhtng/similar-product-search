import numpy as np

class Math:
    @staticmethod
    def compute_cosine_similarity(vector1: np.ndarray, vector2: np.ndarray) -> np.float32:
        """Computing Similarity between two faces.

        Args:
            vector1 (np.ndarray): Face features.
            vector2 (np.ndarray): Face features.

        Returns:
            np.float32: Cosine similarity between face features.
        """
        vector1 = vector1.ravel()
        vector2 = vector2.ravel()
        similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

        return similarity