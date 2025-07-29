from interface import VectorStorage as VectorStorageInterface
from typing import List, Dict, Any
import uuid
import numpy as np
from redis import Redis
from redis.commands.search.field import VectorField, TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import yaml
from utils import PathHelper

class RedisVectorStorage(VectorStorageInterface):
    def __init__(self):
        config_path = PathHelper.get_config_file('redis_config.yaml')

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        self.redis_client = Redis(
            host=config['redis']['host'],
            port=config['redis']['port'],
            decode_responses=False
        )

        self.index_name = config['redis']['index_name']
        self.prefix = config['redis']['prefix']
        self.vector_dim = config['redis']['vector_dim']
        self.distance_metric = config['redis']['distance_metric']
        self.algorithm = config['redis']['algorithm']

        self._create_index()

    def _create_index(self) -> None:
        """
        Create or recreate a Redisearch index for vector storage with metadata fields.
        """

        try:
            info = self.redis_client.ft(self.index_name).info()
            if info['index_name'] == self.index_name:
                print(f"Index '{self.index_name}' already exists")
                return

        except Exception:
            pass

        embedding_field_attributes = {
            'TYPE': 'FLOAT32',
            'DIM': self.vector_dim,
            'DISTANCE_METRIC': self.distance_metric,
        }

        textual_field = VectorField(
            name='textual_embedding',
            algorithm=self.algorithm,
            attributes=embedding_field_attributes
        )

        visual_field = VectorField(
            name='visual_embedding',
            algorithm=self.algorithm,
            attributes=embedding_field_attributes
        )

        schema = (
            textual_field,
            visual_field,
            TextField("animal"),
            TextField("caption"),
            TextField("image_path"),
        )

        try:
            self.redis_client.ft(self.index_name).create_index(
                fields=schema,
                definition=IndexDefinition(
                    prefix=[f"{self.prefix}:"],
                    index_type=IndexType.HASH
                )
            )
            print(f"Created index '{self.index_name}' with updated schema.")
        except Exception as err:
            print(f"Failed to create index: {err}")

    def insert(
        self,
        textual_embedding: np.ndarray,
        visual_embedding: np.ndarray,
        metadata: Dict[str, Any] = {}
    ) -> str:
        """
        Store embeddings and metadata under a new hash key.
        """
        textual = self.embedding_to_bytes(textual_embedding)
        visual = self.embedding_to_bytes(visual_embedding)
        key_id = str(uuid.uuid4())
        redis_key = f"{self.prefix}:{key_id}"

        mapping = {
            'textual_embedding': textual,
            'visual_embedding': visual,
            'animal': metadata.get('animal', ''),
            'caption': metadata.get('caption', ''),
            'image_path': metadata.get('image_path', ''),
        }

        self.redis_client.hset(redis_key, mapping=mapping)

        return key_id

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        embedding_type: str = 'textual'
    ) -> List[Dict[str, Any]]:
        """
        Perform KNN search on specified vector field and return top results with metadata.
        """

        field = 'textual_embedding' if embedding_type == 'textual' else 'visual_embedding'

        query = (
            Query(f"*=>[KNN {top_k} @{field} $vec AS vector_distance]")
                .return_fields("animal", "caption", "image_path", "vector_distance")
                .sort_by("vector_distance")
                .dialect(2)
        )

        query_vector = self.embedding_to_bytes(query_vector)

        if query_vector is None:
            return []

        result = self.redis_client.ft(self.index_name).search(
            query,
            query_params={
                'vec': query_vector
            }
        )

        # Convert Redis documents to dicts
        results_as_dict = []
        for doc in result.docs:
            results_as_dict.append({
                'animal': doc.animal,
                'caption': doc.caption,
                'image_path': doc.image_path,
                'vector_distance': float(doc.vector_distance)
            })

        # example return: [{'animal': 'tiger', 'caption': 'a tiger standing on a red bench in a zoo', 'image_path': 'dataset/animal_images/tiger/712d7f2306.jpg', 'vector_distance': 0.0}]
        return results_as_dict

    def embedding_to_bytes(self, embedding: np.ndarray) -> bytes:
        """
        Convert the embedding to bytes.
        """

        return embedding.astype(np.float32).tobytes()