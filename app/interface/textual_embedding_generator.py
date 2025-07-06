from abc import ABC, abstractmethod

class TextualEmbeddingGenerator(ABC):
    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate a embedding from the given text.
        
        Args:
            text (str): The input text to generate embedding for
            
        Returns:
            list[float]: A list of floating-point numbers representing the textual embedding
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        pass