from indexing.base import BaseIndexer, IndexerCreator
from typing import List, Tuple
from uuid import UUID
import numpy as np
import heapq

class BruteForceIndexer(BaseIndexer):
	def __init__(self):
		self.vectors = {}

	def add(self, vector_id: UUID, vector: List[float]) -> None:
		self.vectors[vector_id] = np.array(vector)
	
	def knn_search(self, query_vector: List[float], k: int) -> List[Tuple[UUID, float]]:
		# result stores each vector id and their similarity with the query vector
		heap = []
		heapq.heapify(heap)
		qv = np.array(query_vector)
		mod_qv = np.sqrt(np.sum(qv**2))
		for vec_id, v in self.vectors.items():
			mod_v = np.sqrt(np.sum(v**2))
			denom = mod_v * mod_qv
			if denom < 1e-12:
				sim = 0
			else:
				sim = np.dot(v,qv) / denom 
			
			if len(heap) < k:
				heapq.heappush(heap, (-sim,vec_id))
			else:
				heapq.heappushpop(heap, (-sim,vec_id))	
		
		return [(vid,-sim) for sim,vid in heap]	
	
	def remove(self, vector_id: UUID) -> None:
		self.vectors.pop(vector_id)

class BruteForceIndexerCreator(IndexerCreator):
	def create_indexer(self) -> BaseIndexer:
		return BruteForceIndexer()
