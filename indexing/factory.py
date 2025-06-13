from indexing.base import BaseIndexer
from indexing.brute_force import BruteForceIndexer
from indexing.kdtree import KDTreeIndexer
from indexing.lsh import LSHIndexer

def get_indexer(indexer_type: str) -> BaseIndexer:
	if indexer_type == 'brute force':
		return BruteForceIndexer()
	elif indexer_type == 'kd tree':
		return KDTreeIndexer()
	elif indexer_type =='lsh':
		return LSHIndexer()
	else:
		raise ValueError(f"Unknown indexer type: {indexer_type}")
