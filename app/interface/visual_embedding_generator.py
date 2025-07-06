from abc import ABC, abstractmethod
from PIL import Image

class VisualEmbeddingGenerator(ABC):
    @abstractmethod
    def generate_embedding(self, image: Image) -> list[float]:
        """
        Generate a embedding from the given image.
        
        Args:
            text (str): The input text to generate embedding for
            
        Returns:
            list[float]: A list of floating-point numbers representing the visual embedding
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        pass