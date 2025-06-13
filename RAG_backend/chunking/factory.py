from typing import Optional
from chunking.fixed_chunker import FixedSizeChunker
from chunking.sentence_chunker import SentenceChunker
from chunking.base import BaseChunker

def get_chunker(chunker_type: str, chunk_size: Optional[int] = None) -> BaseChunker:
    if chunker_type == "fixed":
        return FixedSizeChunker(chunk_size=chunk_size or 200)
    elif chunker_type == "sentence":
        return SentenceChunker()
    else:
        raise ValueError(f"Unknown chunker type: {chunker_type}")

