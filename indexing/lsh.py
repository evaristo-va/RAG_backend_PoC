from indexing.base import BaseIndexer, IndexerCreator
from typing import List, Tuple
from uuid import UUID
import numpy as np
import heapq
from collections import defaultdict

class LSHIndexer(BaseIndexer):
	def __init__(self, num_tables: int = 5, num_hashes: int = 10):
		self.vectors = {}
		self.num_tables = num_tables
		self.num_hashes = num_hashes
		self.planes = None
		self.hash_tables = None

	def _init_planes_tables(self, dim:int):
		# list of lists of random planes for each hashtable
		self.planes = [[np.random.randn(dim) for _ in range(self.num_hashes)] for _ in range(self.num_tables)]
		# hashtables: list of hashtables with a defaultdict with sets (avoid redundancies)
		self.hash_tables = [defaultdict(set) for _ in range(self.num_tables)]

	# generate each bit of hashcode based on side of hyperplane
	def _hash(self, vector: np.array, table_idx: int) -> str:
		return ''.join(['1' if np.dot(vector, plane) >= 0 else '0' for plane in self.planes[table_idx]])

	def add(self, vector_id: UUID, vector: List[float]) -> None:
		if self.planes is None:
			dim = len(vector)
			self._init_planes_tables(dim)

		self.vectors[vector_id] = np.array(vector)
		for i in range(self.num_tables):
			hashcode = self._hash(self.vectors[vector_id],i)
			# add the vectors to their buckets with the hashcode
			self.hash_tables[i][hashcode].add(vector_id)

	def knn_search(self, query_vector: List[float], k: int) -> List[Tuple[UUID, float]]:
		qv = np.array(query_vector)
		mod_qv = np.sqrt(np.sum(qv**2))
		# set to store the possible nearest vectors within all the tables corresponding bucket
		candidate_vecs = set()
		for i in range(self.num_tables):
			hashcode = self._hash(qv,i)
			# using get(key,default) to avoid raising errors
			candidate_vecs.update(self.hash_tables[i].get(hashcode, set()))

		heap = []
		heapq.heapify(heap)

		for vec_id in candidate_vecs:
			v = self.vectors[vec_id]
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
		if vector_id not in self.vectors:
			return 
		v = self.vectors.pop(vector_id)
		for i in range(self.num_tables):
			hashcode = self._hash(v,i)
			self.hash_tables[i][hashcode].discard(vector_id)

class LSHIndexerCreator(IndexerCreator):
	def __init__(self, num_tables=5, num_hashes=10):
		self.num_tables = num_tables
		self.num_hashes = num_hashes

	def create_indexer(self) -> BaseIndexer:
		return LSHIndexer(self.num_tables, self.num_hashes)
