from typing import List
from chunking.base import BaseChunker, ChunkerCreator

class FixedSizeChunker(BaseChunker):
	def __init__(self, chunk_size: int = 200):
		self.chunk_size = chunk_size

	def chunk(self, text: str) -> List[str]:
		chunks = []
		for i in range(0, len(text), self.chunk_size):
			chunks.append(text[i:i+self.chunk_size])
		return chunks

class FixedSizeChunkerCreator(ChunkerCreator):
	def __init__(self, chunk_size: int = 200):
		self.chunk_size = chunk_size

	def create_chunker(self) -> BaseChunker:
		return FixedSizeChunker(self.chunk_size)
