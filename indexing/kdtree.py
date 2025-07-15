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

	def _insert_node(self, node: Optional["KDTreeNode"], vector_id: UUID, vector: np.array, depth: int) -> KDTreeNode:
		n_dim = len(vector)
		axis = depth % n_dim
		if node is None:
        		return KDTreeNode(vector_id, vector, axis)

		# Decide direction based on axis value
		if vector[axis] < node.vector[axis]:
			node.left = self._insert_node(node.left, vector_id, vector, depth + 1)
		else:
			node.right = self._insert_node(node.right, vector_id, vector, depth + 1)
		return node

	def _find_min(self, node: Optional["KDTreeNode"], dim:int, depth: int) -> Optional["KDTreeNode"]:
		if node is None:
			return None

		n_dim = len(node.vector)
		axis = depth % n_dim

		# we are at the node that split along dimension axis
		if axis == dim:
			if node.left is None:
				return node
			return self._find_min(node.left, dim, depth + 1)
		# we search on both subtrees
		else:
			left_min = self._find_min(node.left, dim, depth + 1)
			right_min = self._find_min(node.right, dim, depth + 1)

			min_node = node
			for candidate in [left_min, right_min]:
				if candidate and candidate.vector[dim] < min_node.vector[dim]:
					min_node = candidate
			return min_node
	
	def _remove_node(self, node: Optional["KDTreeNode"], vector_id: UUID, depth: int) -> Optional["KDTreeNode"]:
		if node is None:
			return None

		n_dim = len(node.vector)
		axis = depth % n_dim
		
		if node.vector_id == vector_id:
			if node.right:
				# find the minimum node in the right subtree to replace current node
				min_node = self._find_min(node.right, axis, depth + 1)
				# replace the node with the minimum node
				node.vector_id = min_node.vector_id
				node.vector = min_node.vector
				# remove recursively the minimum node from the right subtree
				node.right = self._remove_node(node.right, min_node.vector_id, depth + 1)
				return node
			elif node.left:
				min_node = self._find_min(node.left, axis, depth + 1)
				node.vector_id = min_node.vector_id
				node.vector = min_node.vector
				node.right = self._remove_node(node.left, min_node.vector_id, depth + 1)
				node.left = None
				return node
			# leaf node (deletion)
			else:
				return None

		target_vector = self.vectors[vector_id]

		if target_vector[axis] < node.vector[axis]:
			node.left = self._remove_node(node.left, vector_id, depth + 1)
		else:
			node.right = self._remove_node(node.right, vector_id, depth + 1)

		return node

	def add(self, vector_id: UUID, vector: List[float]) -> None:
		self.vectors[vector_id] = np.array(vector)
		self.root = self._insert_node(self.root, vector_id, np.array(vector), 0)
	
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
		if vector_id not in self.vectors:
			return
		self.root = self._remove_node(self.root, vector_id, 0)
		self.vectors.pop(vector_id)

class KDTreeIndexerCreator(IndexerCreator):
	def create_indexer(self) -> BaseIndexer:
		return KDTreeIndexer()
