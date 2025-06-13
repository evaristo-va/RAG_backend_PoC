from abc import ABC, abstractmethod
from typing import List, Tuple
from uuid import UUID

class BaseIndexer(ABC):
    @abstractmethod
    def add(self, vector_id: UUID, vector: List[float]) -> None:
        """Add vectors with their IDs to the index."""
        pass

    @abstractmethod
    def knn_search(self, query_vector: List[float], k: int) -> List[Tuple[UUID, float]]:
        """Search top-k nearest neighbors. Returns list of (id, distance)."""
        pass

    @abstractmethod
    def remove(self, vector_id: UUID) -> None:
        """Remove vectors by their IDs."""
        pass

class IndexerCreator(ABC):
    @abstractmethod
    def create_indexer(self) -> BaseIndexer: 
        pass  
