from typing import List
from chunking.base import BaseChunker, ChunkerCreator
import re

class SentenceChunker(BaseChunker):
	def __init__(self):
		pass

	def chunk(self, text: str) -> List[str]:
		chunks = re.split(r'(?<=[.!?])\s+', text.strip())
		return chunks

class SentenceChunkerCreator(ChunkerCreator):
	def create_chunker(self) -> BaseChunker:
		return SentenceChunker()
