from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from uuid import UUID, uuid4


class SearchQueryRequest(BaseModel):
	query: str = Field(..., description='query to perform search')
	k: int = Field(5, description='number of results to retreive')
	date_range: Optional[Tuple[datetime,datetime]] = Field(None, description='Filter by date as tuple (from_date,to_date) to filter by timestamp')

class SearchResultResponse(BaseModel):
	chunk_id: UUID
	document_id: UUID
	score: float
	content: str
	metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description='Metadata')

class CreateDocumentRequest(BaseModel):
	library_id: UUID
	title: str  
	content: str 
	metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description='Metadata')

class CreateLibraryRequest(BaseModel):
    name: str = Field(..., description="Name of the library")
    description: Optional[str] = Field(None, description="Library description")
    metadata: Optional[Dict[str, Optional[str]]] = Field(default_factory=dict)
