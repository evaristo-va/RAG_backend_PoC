# 🧠 RAG Backend

This is a PoC backend service for Retrieval-Augmented Generation (RAG) that handles document ingestion, chunking, embedding and vector indexing. It includes robust in-memory data structures and exposes CR(U)D operations along with search functionality through APIs powered by FastAPI and Pydantic.

---

## 🚀 Overview

The core data structures and API request/response schemas are defined using **Pydantic**, ensuring:

- ✅ Automatic data validation and parsing  
- 🔁 Serialization of Python objects to JSON  
- 📚 Auto-generation of OpenAPI/Swagger documentation for all API endpoints

This architecture allows for safe, extensible, and efficient document management and semantic search.
> ⚙️ Thread safety: All write operations to the in-memory database are protected using thread locks to prevent data races and ensure consistency during concurrent access.
---

## 📦 Data Model

The system revolves around three main entities:

- **Library**  
  Object representing a collection documents. Stores a list of associated `Document` UUIDs. Contains name, description and metadata.
  
- **Document**  
  Object representing a collection of document chunks. Stores title, full text content and metadata. Holds a list of associated `Chunk` UUIDs. Linked to a `Library` UUID.

- **Chunk**  
  A semantically meaningful segment of a document. Stores the text content and metadata. Linked to a `Document` UUID.

All entities are stored in an **in-memory database**, with dictionaries keyed by UUID (universally unique identifier). The actual vector embeddings are stored in a vector index as a dictionary keyed by the `Chunk` UUID, decoupling the semantic search logic from the core data model.

---

## 🧬 Project Structure
```
RAG_backend/
├── main.py                  # FastAPI app entry point and initial example library and docs creation
├── db.py                    # In-memory DB, indexer initalization and thread-safe operations
├── models.py                # Core data models (Library, Document, Chunk)
├── schemas.py               # Pydantic schemas for requests/responses
├── Dockerfile               # Docker file

├── routes/                  # FastAPI endpoint definitions
│   ├── library.py
│   ├── document.py
│   └── search.py

├── services/                # Core logic
│   ├── library_service.py
│   ├── documents_service.py
│   └── search_service.py

├── indexing/                # Vector indexer implementations and factory
│   ├── base.py
│   ├── brute_force.py
│   ├── kdtree.py
│   └── factory.py

├── chunking/                # Chunking implementations and factory
│   ├── base.py
│   ├── fixed.py
│   └── factory.py

├── embedding/               # Embedding wrapper (e.g. Cohere)
│   └── embedder.py

├── data/                    # Sample documents
│   ├── cristiano_ronaldo.txt
│   ├── leo_messi.txt
│   └── rafa_nadal.txt

└── requirements.txt         # Code dependencies
```

### 📁 `db.py`
- Initializes the in-memory `DB` class.
- Creates the global vector `indexer`.
- Implements thread locking for safe concurrent access.

### 📁 `indexing/`
- Vector index implementations (e.g. brute force, KD-tree and local sensitivity hashing) and storage of embeddings.
- Follows a **factory pattern** for easily switching/adding index types.

### 📁 `embedding/`
- Interfaces with **Cohere API** to generate vector embeddings.
- Embeddings can be computed for both document chunks and search queries.

### 📁 `chunking/`
- Chunking implementations (e.g. fixed-length, sentence-based).
- Follows a **factory design pattern** for easily switching/adding new chunking methods.

### 📁 `services/`
- Encapsulates core business logic: creating/deleting documents/libraries, searching, etc.
- Operates on validated Pydantic schemas.
- Keeps logic independent of HTTP layer.

### 📁 `routes/`
- Defines FastAPI endpoints.
- Handles routing, request parsing, and response formatting.
- Delegates logic to `services`.

---

## 📑 API Usage & Endpoints
### 🖥️ Run locally
```
uvicorn main:app --reload
```
❗️Note: the api key should be in an .env file inside embedding as COHERE_API_KEY
### ✍️ Create a Document
Endpoint POST /create-document/
```
{
  "library_id": "LIBRARY_UUID_HERE",
  "title": "Quantum Physics",
  "content": "Quantum physics studies the behavior of matter and energy at the smallest scales.",
  "metadata": {}
}
```
cURL:
```
curl -X POST http://localhost:8000/create-document/ \
  -H "Content-Type: application/json" \
  -d '{"library_id": <library_id>, "title": <title>, "content": <content>, "metadata": {}}'
```
### 🗑️ Delete a Document
Endpoint DELETE /documents/{document_id}

cURL:
```
curl -X DELETE http://localhost:8000/documents/<document_id>
```

### 👀 Read a Document
Endpoint DELETE /documents/{document_id}

cURL:
```
curl http://localhost:8000/documents/<document_id>
```
### 🔎 Search for k chunks (allows for date filterint)
Endpoint POST /search-document/
```
{
  "query": <query>,
  "k": <top_k>,
  "date_range: (<from_date>,<to_date>)   (Optional)
  
}
```

cURL

```
curl -X POST http://localhost:8000/search-document/ \
  -H "Content-Type: application/json" \
  -d '{"query": <query>, "top_k": <top_k>}'
```

### ✍️ Create a Library
Endpoint POST /create-library/
```
{
  "name": <name>,
  "description": <description>
  "metadata": {<metadata_dict>}  (Optional)  
}
```
cURL:
```
curl -X POST http://localhost:8000/create-library/ \
  -H "Content-Type: application/json" \
  -d '{"name": <name>, "description": <description>, "metadata": {<metadata_dict>}}'
```

### 🗑️ Delete a Library
Endpoint DELETE /libraries/{library_id}

cURL:
```
curl -X DELETE http://localhost:8000/libraries/<library_id>
```
Try with library_id="838da7d4-73aa-4463-998d-b62e6b27afcd" (Already created by default in main)
### 👀 Read a Library (All associated documents)
Endpoint GET /libraries/{library_id}

cURL:
```
curl -X GET http://localhost:8000/libraries/<library_id>
```

## 👷🏼‍♂️ Algorithmic choices for Indexing
Let:
- N: number of data points
- D: dimension of each vector (data point)
- H: number of random hyperplanes in LSH
- L: number of hashtables
- K: number of KNN for search
### 🔨 Brute force approach
-  Knn search : complexity is O(nd+nlogk) with d being embedding vector dimension, k the numer of elements to retrieve (heap size).
-  Add/delete: constant operations O(1) implemented via hashmap.

<div align="center">
  <img src="https://github.com/user-attachments/assets/35adc6d6-d9e0-49d7-81d0-640e4c41cafd" width="400"/>
</div>
  
### 🌳 K-dimensional trees (Kdtrees)
Main idea is to partition the space hierarchically into hypercubes using a tree-like structure. Each node in the tree contains an axis or dimension to split the data in half according to the median.
-  Knn search: Complexity is O(log<sub>2</sub>N·[D+log<sub>2</sub>K])~O(log<sub>2</sub>N) on average. If tree is balanced the traversal is O(log<sub>2</sub>N) and the heap maintenance is O(log<sub>2</sub>K). For high dimensions however O(N·log<sub>2</sub>K).
-  Delete: O(log<sub>2</sub>N).
-  Add: to add we traverse down the tree O(log<sub>2</sub>N).

<div align="center">
  <img src="https://github.com/user-attachments/assets/ae8d8e98-dc04-4a4a-97ca-fe3560e01265" width="400"/>
</div>

### #️⃣ Local sensitivity hashing (LSH)
The main idea is to partition the space using H random hyperplanes. Based on those hyperplanes the data is divided into buckets using a hashcode generated based on where a point is using the hyperplanes.

-  Knn search: Complexity is O(L·H·D + L·N/2^H (D+log<sub>2</sub> K)). On average if we set H=Log<sub>2</sub>(N) then complexity is O(L·D·Log<sub>2</sub>N)
-  Add: O(H·D), in reality due to planes initialization is O(H·D·L).
-  Delete: O(L·H·D).
  
<div align="center">
  <img src="https://github.com/user-attachments/assets/d3c7326d-3699-4fec-a6e4-ab439e464b6a" width="400"/>
</div>


---


## ✅ Features

- In-memory DB 
- Multiple indexing (Brute Force, KD-Tree, LSH) and chunking (fixed-length, sentence-based) strategies.
- Pluggable embedding service (Cohere by default)
- Thread-safe read/write operations
- Auto-generated OpenAPI docs (View on Swagger UI)

---

## 🛠️ Requirements

- Python 3
- FastAPI
- Uvicorn
- Pydantic
- Cohere SDK
- Numpy

## 📌 Future improvements
- Allow for search within specific libraries and metadata filtering (besides the date filtering).
- Possibility of selecting the indexing and chunking methods by the user dynamically.
- Defining schemas for the responses.
- Create update endpoints/functions.
- Algorithmic improvements: Insert node into tree instead of rebuilding the kdtree each times for efficiency. Improve treebuilder with an efficient algorithm to find the median instead of doing a sort.
