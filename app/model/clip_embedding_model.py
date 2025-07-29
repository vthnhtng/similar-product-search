from interface import EmbeddingModel as EmbeddingModelInterface
from clip_client import Client
import numpy as np
import yaml
from utils import PathHelper

class CLIPEmbeddingModel(EmbeddingModelInterface):
    def __init__(self):
        config_path = PathHelper.get_config_file('CLIP_config.yaml')

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        server_url = f"{config['server']['host']}:{config['server']['port']}"
        self.client = Client(server_url)

    def embed_text(self, text: str) -> np.ndarray:
        """
        Extract an embedding from the text.

        Args:
            text (str): Input text.

        Returns:
            np.ndarray: The text embedding (feature vector).
        """
        return self.client.encode([text])

    def embed_image(self, image_path: str) -> np.ndarray:
        """
        Extract an embedding from the image.

        Args:
            image_path (str): Input image path.

        Returns:
            np.ndarray: The image embedding (feature vector).
        """
        return self.client.encode([image_path])
