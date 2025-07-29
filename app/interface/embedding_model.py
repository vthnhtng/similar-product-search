from abc import ABC, abstractmethod
import numpy as np

class EmbeddingModel(ABC):
    """
    Interface for a face recognizer that extracts facial embeddings.
    """

    @abstractmethod
    def embed_text(self, text: str) -> np.ndarray:
        """
        Extract an embedding from the text.
        
        Args:
            text (str): Input text.

        Returns:
            np.ndarray: The text embedding (feature vector).
        """

    @abstractmethod
    def embed_image(self, image_path: str) -> np.ndarray:
        """
        Extract an embedding from the image.

        args:
            image (np.ndarray): Input image.

        Returns:
            np.ndarray: The image embedding (feature vector).
        """
