from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4

class Chunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    content: str = Field(..., description='Chunk text')
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description='Metadata')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp')

class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    library_id: UUID
    title: str
    content: str = Field(..., description='Document text')
    chunks: List[UUID] = Field(default_factory=list, description='Chunks IDs for a document')
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description='Metadata')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp')

class Library(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = Field(default=None, description='Description of the library')
    document_ids: List[UUID] = Field(default_factory=list, description='Documents IDs')
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description='Metadata')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp')
