from fastapi import FastAPI
from uuid import UUID
from models import Library
from db import db
from routes.document import router as document_router
from routes.library import router as library_router
from routes.search import router as search_router
from schemas import CreateDocumentRequest
from services.documents_service import create_document

app = FastAPI()

app.include_router(document_router)
app.include_router(search_router)
app.include_router(library_router)

@app.on_event("startup")
def create_sample_library():
	lib_id = UUID("838da7d4-73aa-4463-998d-b62e6b27afcd")
	db.libraries[lib_id] = Library(
	id=lib_id,
	name="Example Library",
	description="A library for testing"
	)
	print(f"Library created with ID: {lib_id}")

	document_paths=['data/cristiano_ronaldo.txt', 'data/leo_messi.txt', 'data/rafa_nadal.txt']

	for index, path in enumerate(document_paths):
		with open(path, 'r') as f:
			file_content = f.read()

		document_request = CreateDocumentRequest(
			library_id = lib_id,
			title = f'Sample Document {index}',
			content = file_content,
			metadata = {}
			)
	
		document = create_document(db, document_request)
		print(f"Document {index} created with ID: {document.id}")
