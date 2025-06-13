from models import Library
from db import DB, db, indexer
from uuid import UUID, uuid4
from datetime import datetime
from embedding.embedder import vector_embedder
from indexing.factory import get_indexer
from chunking.factory import get_chunker
from schemas import CreateLibraryRequest
from typing import Optional, Dict, List, Any
from fastapi import HTTPException

def create_library(db: DB, request: CreateLibraryRequest) -> Library:
	# logic of the function to be wrapped up into lock trheading
	def f():
		for lib in db.libraries.values():
			if lib.name == request.name:
				raise HTTPException(status_code=400, detail=f"Library with name '{request.name}' already exists.")

		# generate document id and timestamp
		lib_id = uuid4()
		timestamp = datetime.now()
		
		# create library object
		library = Library(
		    id = lib_id,
		    name = request.name,
	  	    description = request.description,
		    metadata = request.metadata or {},
		    document_ids = [],
		    timestamp = timestamp
		)
		
		db.libraries[library.id]=library
		
		return library 
	
	return db.lock_write(f)

def read_library(db: DB, library_id: UUID):
	if library_id not in db.libraries:
		raise HTTPException(status_code=404, detail=f"Library ID {library_id} not found.")
		
	document_ids = db.libraries[library_id].document_ids
	
	return [db.documents[doc_id] for doc_id in document_ids]

def delete_library(db: DB, library_id: UUID):
	def f():
		if library_id not in db.libraries:
			raise HTTPException(status_code=404, detail=f"Library ID {library_id} does not exist.")
		# remove library from db
		library = db.libraries.pop(library_id)
		document_ids = library.document_ids

		for doc_id in document_ids:
			document = db.documents.pop(doc_id)
			
			# remove chunks
			for chunk_id in document.chunks:
				db.chunks.pop(chunk_id)
				indexer.remove(chunk_id)

		return {"detail": f"Library {library_id} and all its documents deleted successfully."}

	return db.lock_write(f)
