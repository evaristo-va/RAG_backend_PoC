from fastapi import APIRouter, HTTPException
from db import db
from schemas import CreateDocumentRequest
from services.documents_service import create_document
from services.documents_service import delete_document
from services.documents_service import read_document
from uuid import UUID

router = APIRouter(prefix="/documents")

@router.post("/")
def create_document_endpoint(request: CreateDocumentRequest):
	return create_document(db, request)

@router.delete("/{document_id}")
def delete_document_endpoint(document_id: UUID):
	return delete_document(db, document_id)

@router.get("/{document_id}")
def read_document_endpoint(document_id: UUID):
	return read_document(db, document_id)
