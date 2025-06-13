from models import Chunk, Document, Library
from typing import Dict
from uuid import UUID
from threading import Lock
from indexing.factory import get_indexer

class DB:
    def __init__(self):
        self.libraries: Dict[UUID, Library] = {}
        self.documents: Dict[UUID, Document] = {}
        self.chunks: Dict[UUID, Chunk] = {}
        self.lock = Lock()

    # Wrapper to avoid data races in write operations.
    def lock_write(self, func):
        with self.lock:
            return func()

db = DB()
indexer = get_indexer("kd tree")
#indexer = get_indexer("brute force")
