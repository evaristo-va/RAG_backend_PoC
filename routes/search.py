from fastapi import APIRouter
from db import db
from schemas import SearchQueryRequest, SearchResultResponse
from services.documents_service import search_documents

router = APIRouter(prefix="/documents")

@router.post("/search")
def search_documents_endpoint(request: SearchQueryRequest):
	results = search_documents(db, request)
	response = []
	for chunk, score in results:
		response.append(SearchResultResponse(
			chunk_id=chunk.id,
			document_id=chunk.document_id,
			score=score,
			content=chunk.content,
			metadata=chunk.metadata or {}
			))
			
	return response
