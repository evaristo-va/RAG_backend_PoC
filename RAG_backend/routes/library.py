from fastapi import APIRouter
from db import db
from schemas import CreateLibraryRequest
from services.library_service import create_library
from services.library_service import delete_library
from services.library_service import read_library
from uuid import UUID

router = APIRouter()

@router.post("/create-library/")
def create_library_endpoint(request: CreateLibraryRequest,):
    return create_library(db, request)

@router.delete("/libraries/{library_id}")
def delete_library_endpoint(library_id: UUID):
	return delete_library(db, library_id)

@router.get("/libraries/{library_id}")
def read_library_endpoint(library_id: UUID):
	return read_library(db, library_id)
