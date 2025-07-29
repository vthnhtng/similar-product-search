from model import *
from utils import PathHelper
import yaml

class SearchSystemFactory:
    CONFIG_FILE_NAME = 'search_system.yaml'

    def __init__(self):
        config_path = PathHelper.get_config_file(self.CONFIG_FILE_NAME)
        self.config = yaml.safe_load(open(config_path))

    def create(self):
        type = self.config['type']
        match type:
            case 'default':
                redis_vector_storage = RedisVectorStorage()
                clip_embedding_model = CLIPEmbeddingModel()

                return SearchSystem(
                    redis_vector_storage,
                    clip_embedding_model, 
                    clip_embedding_model
                )
