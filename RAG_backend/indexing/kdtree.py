from indexing.base import BaseIndexer, IndexerCreator
from typing import List, Tuple, Dict, Optional
from uuid import UUID
import numpy as np
import heapq

class KDTreeNode:
	def __init__(self, vector_id: UUID, vector: np.array, axis: int, left: Optional["KDTreeNode"]=None, right: Optional["KDTreeNode"]=None):
		self.vector_id = vector_id
		self.vector = vector
		self.axis = axis
		self.left = left
		self.right = right

class KDTreeBuilder:
	def build(self, vectors: Dict[UUID, np.array]) -> Optional["KDTreeNode"]:
		items = list(vectors.items())
		n_dim = len(items[0][1])

		def recursive_build(items: List[Tuple[UUID, np.array]], depth=0) -> Optional["KDTreeNode"]:
			# base case
			if not items:
				return
			axis = depth % n_dim
			# sort and compute median
			items.sort(key=lambda x:x[1][axis])
			median_idx = len(items) // 2
			median = items[median_idx]

			# build left and right subtrees cycling splitting coordinate
			left = recursive_build(items[:median_idx], depth+1)
			right = recursive_build(items[median_idx+1:], depth+1)
			return KDTreeNode(median[0],median[1],axis,left,right)

		return recursive_build(items)

class KDTreeIndexer(BaseIndexer):
	def __init__(self):
		self.vectors = {}
		self.root: Optional["KDTreeNode"] = None
		self.builder = KDTreeBuilder()

	def add(self, vector_id: UUID, vector: List[float]) -> None:
		self.vectors[vector_id] = np.array(vector)
		# as of now we rebuild tree with each add
		self.root = self.builder.build(self.vectors)
	
	def knn_search(self, query_vector: List[float], k: int) -> List[Tuple[UUID, float]]:
		# result stores each vector id and their similarity with the query vector
		heap = []
		heapq.heapify(heap)
		qv = np.array(query_vector)

		def search(node: Optional["KDTreeNode"]):
			if not node:
				return
			v, axis = node.vector, node.axis
			vec_id = node.vector_id
			# distance between query point and each plane
			dist = np.sum((v-qv)**2)
			# keep track of k best distances found so far
			if len(heap) < k:
				heapq.heappush(heap, (-dist,vec_id))
			else:
				heapq.heappushpop(heap, (-dist,vec_id))
			
			diff = qv[axis] - v[axis]

			# decide if going left or right on the tree
			if diff < 0:
				near, far = (node.left,node.right)
			else:	
				near, far = (node.right,node.left)
		
			search(near)
		
			# if we have not found k neighbors yet or the distance to splitting plane is shorter than 
			# the worst of our current knn section we did not visit might contain a nearest neighbro	
			if len(heap) < k or diff**2 < -heap[0][0]:
				search(far)

		search(self.root)
		# return k nearest neighbors
		return [(vid,-dist) for dist,vid in heap]
	
	def remove(self, vector_id: UUID) -> None:
		self.vectors.pop(vector_id)

class KDTreeIndexerCreator(IndexerCreator):
	def create_indexer(self) -> BaseIndexer:
		return KDTreeIndexer()
