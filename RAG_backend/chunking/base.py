from abc import ABC, abstractmethod
from typing import List

class BaseChunker(ABC):
	@abstractmethod
	def chunk(self, text: str) -> List[str]:
		pass

class ChunkerCreator(ABC):
	@abstractmethod
	def create_chunker(self) -> BaseChunker:
		pass
