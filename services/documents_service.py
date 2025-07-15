from models import Document, Chunk, Library
from db import DB, db, indexer, chunker
from uuid import UUID, uuid4
from datetime import datetime
from embedding.embedder import vector_embedder
from indexing.factory import get_indexer
from chunking.factory import get_chunker
from schemas import CreateDocumentRequest, SearchQueryRequest
from fastapi import HTTPException
from typing import Optional, Dict, List, Tuple, Any

def create_document(db: DB, request: CreateDocumentRequest) -> Document:
	# Check if the library we are trying to add to exists
	library_id = request.library_id
	#library_id = UUID(request.library_id)
	
	if library_id not in db.libraries:
		raise HTTPException(status_code=404, detail=f"Library with ID {library_id} not found.")

	# get title content and metadata
	title = request.title
	content = request.content
	metadata = request.metadata

	# logic of the function to be wrapped up into lock trheading
	def f():
		# generate document id and timestamp
		doc_id = uuid4()
		timestamp = datetime.now()
		
		# create chunker object
		#chunker = get_chunker("fixed", chunk_size = 200)
		
		# split the text of document into chunks
		chunks_list = chunker.chunk(content)
		chunk_ids = []
		
		for chunk_text in chunks_list:
		    # generate vector embeddings and create chunk object
		    embedding = vector_embedder(chunk_text, input_type='search_document')
		    chunk = Chunk(
		        id=uuid4(),
		        document_id=doc_id,
		        content=chunk_text,
		        embedding_vec=embedding,
		        timestamp=timestamp
		    )
		
		    # add chunks to database
		    db.chunks[chunk.id] = chunk
		    chunk_ids.append(chunk.id)
		    # add chunks to index
		    indexer.add(chunk.id, embedding)
		
		# create document object
		document = Document(
		    id = doc_id,
		    library_id = library_id,
		    title = title,
		    content = content,
		    chunks = chunk_ids,
		    timestamp = timestamp
		)
		
		# add document object to database
		db.documents[doc_id] = document 
		# add documents to the library in the database
		db.libraries[library_id].document_ids.append(doc_id)
		print(f'Document with ID "{doc_id}" created successfully')
		
		return document 
	
	return db.lock_write(f)

def read_document(db:DB, document_id: UUID) -> Document:
	document = db.documents.get(document_id)
	if not document:
		raise HTTPException(status_code=404, detail=f"Document ID {document_id} not found.")
	return document

def delete_document(db:DB, document_id: UUID):
	if document_id not in db.documents:
		raise HTTPException(status_code=404, detail=f"Document ID {document_id} does not exist.")

	def f():
		# remove document from db
		document = db.documents.pop(document_id)
		# remove chunks from db and index
		for chunk_id in document.chunks:
			if chunk_id in db.chunks:
				db.chunks.pop(chunk_id)
				indexer.remove(chunk_id)
		# remove document id from library	
		library_id = document.library_id
		if library_id in db.libraries:
			library = db.libraries[library_id]
			if document_id in library.document_ids:
				library.document_ids.remove(document_id)

		return {"detail": f"Document {document_id} deleted successfully."}

	return db.lock_write(f)
				

def search_documents(db: DB, request: SearchQueryRequest) -> List[Tuple[Chunk,float]]:
	query_embedding = vector_embedder(request.query, input_type='search_query')

	# This gives a tuple of (chunk_id,similarity_score)
	top_k_results = indexer.knn_search(query_embedding, request.k)

	# return 
	k_chunks = [(db.chunks.get(chunk_id),score) for chunk_id, score in top_k_results]
	
	# filter by dates
	if request.date_range:
		from_date, to_date = request.date_range
		k_chunks = [(chunk,score) for chunk, score in k_chunks if from_date <= chunk.timestamp <= to_date]

	return k_chunks
