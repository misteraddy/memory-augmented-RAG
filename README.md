# Memory Augmented RAG

A FastAPI-based retrieval-augmented generation system that augments LLM responses with persistent user memory, short-lived session memory, and semantic recall over a knowledge base. The project is designed for document-grounded Q&A with memory-aware behavior, making it useful for assistant-style chat systems, internal knowledge bots, and user-specific conversational experiences.

## Overview

This project combines:

- A vector knowledge base for PDF document retrieval
- MongoDB collections for short-term and long-term memory
- Qdrant collections for semantic memory and conversation recall
- An LLM orchestration layer that builds a memory-aware prompt
- A FastAPI service for exposing the retrieval and health endpoints

The result is a memory-aware question-answering system that can:

- search document chunks from a PDF knowledge base
- include long-term user context in the prompt
- include recent session messages in the prompt
- remember important semantic facts from past interactions
- persist useful memory updates back into storage

## Architecture

At a high level, the request flow looks like this:

```text
User Query
   |
   v
FastAPI endpoint
   |
   v
Retrieval service
   |-- embed query
   |-- query Qdrant knowledge base
   |-- fetch long-term memory (MongoDB)
   |-- fetch short-term memory (MongoDB)
   |-- fetch semantic memory (Qdrant)
   v
LLM prompt assembly
   |
   v
LLM response generation
   |
   +-- save short-term memory
   +-- save long-term memory
   +-- save semantic memory
```

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Motor (async MongoDB client)
- PyMongo
- qdrant-client
- sentence-transformers
- PyMuPDF for PDF parsing
- Google GenAI SDK for LLM calls
- Pydantic + pydantic-settings for settings management

## Project Structure

```text
memory_augmented_rag/
├── api/
│   └── v1/
│       ├── health.py
│       ├── query.py
│       └── router.py
├── core/
│   ├── config.py
│   ├── constants.py
│   └── database.py
├── exception/
│   ├── custom_exception.py
│   ├── handlers.py
│   └── __init__.py
├── ingestion/
│   ├── chunker.py
│   ├── document_loader.py
│   ├── embedder.py
│   └── pipeline.py
├── knowledge_base/
│   └── pdfs/
├── llm/
│   └── client.py
├── models/
├── prompt_library/
│   └── prompt.py
├── repositories/
│   ├── mongodb/
│   │   ├── client.py
│   │   └── memory_repository.py
│   └── qdrant/
│       ├── client.py
│       ├── collection_manager.py
│       ├── knowledge_repository.py
│       └── ...
├── scripts/
│   └── ingest_kb.py
├── schemas/
├── services/
│   ├── generation_service.py
│   ├── ingestion_service.py
│   ├── memory_service.py
│   └── retrieval_service.py
├── utils/
│   └── ids.py
├── .env
├── .gitignore
├── requirements.txt
├── server.py
└── README.md
```

## Key Components

### 1. API Layer

The API layer is built with FastAPI and sits under `/api/v1`.

Relevant files:

- `server.py` creates the app and starts database connections
- `api/v1/health.py` exposes health checks
- `api/v1/query.py` defines the main retrieval endpoint
- `api/v1/router.py` registers routers

The app startup lifecycle opens connections to MongoDB and Qdrant, ensures required collections exist, and closes them when the app shuts down.

### 2. Configuration

Settings are loaded from environment variables and `.env` via `pydantic-settings`.

Important settings include:

- `MONGODB_URI`
- `MONGODB_DATABASE`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION_NAME`
- `QDRANT_SEMANTIC_MEMORY_COLLECTION`
- `EMBEDDING_MODEL`
- `KNOWLEDGE_BASE_PATH`
- `CHUNK_SIZE`
- `CHUNK_OVERLAP`

See `core/config.py` for the full configuration model.

### 3. PDF Knowledge Base Ingestion

The ingestion pipeline loads PDF files, splits them into chunks, embeds the chunks, and stores them in a Qdrant vector collection.

The flow is defined in:

- `ingestion/document_loader.py`
- `ingestion/chunker.py`
- `ingestion/embedder.py`
- `ingestion/pipeline.py`

The script used for ingestion is:

```bash
python scripts/ingest_kb.py
```

This script walks the `knowledge_base/pdfs` directory, ingests all `.pdf` files, and stores the resulting vector chunks in Qdrant.

### 4. Memory System

The project separates memory into three distinct categories:

- Long-term memory: user-specific memory stored in MongoDB
- Short-term memory: recent session interactions stored in MongoDB
- Semantic memory: important remembered context stored as vector embeddings in Qdrant

The MongoDB repository is implemented in `repositories/mongodb/memory_repository.py`.

Collections used:

- `long_term_memory`
- `short_term_memory`

Each document typically contains fields such as:

- `user_id`
- `session_id`
- `query`
- `response`
- `memory`
- `created_at`
- `updated_at`

### 5. Retrieval and Response Generation

The retrieval workflow is orchestrated by `services/retrieval_service.py`.

It does the following:

1. Validates `user_id`, `session_id`, and `query`
2. Embeds the incoming query
3. Queries the Qdrant knowledge collection for similar document chunks
4. Retrieves long-term, short-term, and semantic memory
5. Builds a final prompt using `prompt_library/prompt.py`
6. Calls the LLM with the assembled prompt
7. Saves the response to memory stores

The LLM prompt explicitly tells the model to return valid JSON with:

- `answer`
- `long_term_memories`
- `semantic_memory`

This makes memory extraction and answer generation structured and easy to process.

### 6. LLM Integration

The LLM client is defined in `llm/client.py` and uses the Google GenAI client.

It sends the final prompt to the configured model and expects a textual response.

The embedding model configured by default is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

This is used to create vector embeddings for knowledge-base and semantic-memory retrieval. The actual LLM generation model is configured via the Google GenAI client and should be set according to the environment and model access available to your deployment.

## Environment Variables

Create a `.env` file at the project root. The repository includes an example `.env`, but it may contain masked secrets, so replace any placeholders before running the service.

| Variable | Required | Default | Description |
|---|---:|---|---|
| `APP_NAME` | No | `Memory Augmented RAG` | Friendly application name |
| `APP_ENV` | No | `development` | Environment label |
| `MONGODB_URI` | Yes | — | MongoDB connection string |
| `MONGODB_DATABASE` | No | `memory_augmented_rag` | MongoDB database name |
| `QDRANT_URL` | Yes | — | Qdrant server URL |
| `QDRANT_API_KEY` | Yes | — | Qdrant API key |
| `QDRANT_COLLECTION_NAME` | No | `memory_augmented_knowledge_base` | Knowledge-base vector collection |
| `QDRANT_SEMANTIC_MEMORY_COLLECTION` | No | `conversation_semantic_memory` | Conversation memory vector collection |
| `EMBEDDING_DIMENSION` | No | `384` | Embedding vector size |
| `MONGODB_MAX_POOL_SIZE` | No | `20` | MongoDB pool max size |
| `MONGODB_MIN_POOL_SIZE` | No | `2` | MongoDB pool min size |
| `MONGODB_SERVER_SELECTION_TIMEOUT_MS` | No | `5000` | MongoDB timeout |
| `QDRANT_TIMEOUT` | No | `10` | Qdrant client timeout in seconds |
| `EMBEDDING_MODEL` | No | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model used for vectorization |
| `KNOWLEDGE_BASE_PATH` | No | `knowledge_base/pdfs` | Directory with source PDFs |
| `CHUNK_SIZE` | No | `1000` | Text chunk size |
| `CHUNK_OVERLAP` | No | `150` | Overlap between adjacent chunks |

Example `.env`:

```env
APP_NAME=Memory Augmented RAG
APP_ENV=development

MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
MONGODB_DATABASE=memory_augmented_rag

QDRANT_URL=https://<your-qdrant-host>
QDRANT_API_KEY=<your-qdrant-api-key>
QDRANT_COLLECTION_NAME=memory_augmented_knowledge_base
QDRANT_SEMANTIC_MEMORY_COLLECTION=conversation_semantic_memory

EMBEDDING_DIMENSION=384
MONGODB_MAX_POOL_SIZE=20
MONGODB_MIN_POOL_SIZE=2
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
QDRANT_TIMEOUT=10
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
KNOWLEDGE_BASE_PATH=knowledge_base/pdfs
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
```

## Local Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the required environment file

Make sure the `.env` file exists and contains valid values for your MongoDB and Qdrant services.

### 4. Prepare a knowledge-base directory

Create a PDF directory if it does not yet exist:

```bash
mkdir -p knowledge_base/pdfs
```

Place one or more PDFs in that folder before running ingestion.

## Running the App

Start the server with:

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- `http://localhost:8000/` for app status
- `http://localhost:8000/docs` for FastAPI Swagger UI
- `http://localhost:8000/redoc` for ReDoc

## Ingesting the Knowledge Base

A utility script is included to ingest all PDFs from the configured knowledge-base folder:

```bash
python scripts/ingest_kb.py
```

This script:

- loads PDFs from `knowledge_base/pdfs`
- splits the content into chunks
- embeds each chunk
- stores the chunks in the Qdrant collection defined by `QDRANT_COLLECTION_NAME`

## API Endpoints

### Health check

```http
GET /api/v1/health
```

Returns the status of the MongoDB and Qdrant connections.

### Session query endpoint

The route is defined in `api/v1/query.py`:

```http
POST /api/v1/sessions/{session_id}
```

Expected payload:

```json
{
  "user_id": "user-123",
  "memory_id": "optional-memory-id",
  "query": "What are the key requirements in the onboarding document?"
}
```

The service then:

- embeds the query
- carries out vector search in the knowledge base
- retrieves memory context
- calls the LLM
- stores the output in MongoDB and Qdrant

Note: The query router is defined in `api/v1/query.py` but must be included in `api/v1/router.py` for the endpoint to be served by the app.

## Request Flow Example

A typical query flow might look like:

```json
POST /api/v1/sessions/session-42
{
  "user_id": "user-123",
  "memory_id": "mem-abc",
  "query": "Summarize the compliance guidelines for our product team."
}
```

The system can then:

- pull relevant PDF chunks from the vector store
- recall any prior user preferences or memory
- include both recent session and semantic memory in the prompt
- respond with a direct answer and store the new memory state

## Data Stores

### MongoDB

Used for persistent short- and long-term memory.

Collections:

- `long_term_memory`
- `short_term_memory`

### Qdrant

Used for vector search and semantic memory.

Collections:

- `memory_augmented_knowledge_base`
- `conversation_semantic_memory`

## Notes on Behavior

This project is intentionally designed around retrieval-augmented generation with memory reflection. In practice, it tries to:

- answer based on the most relevant retrieved content
- retain user-specific facts that may matter later
- maintain continuity across conversations
- make future answers more contextual and personalized

## Common Troubleshooting

### 1. Collection not found

Ensure the app startup lifecycle has run and the Qdrant collections have been created. If necessary, run the ingestion script or manually create the collection.

### 2. PDF ingestion fails

Check that:

- the file exists
- the file is a valid PDF
- the knowledge-base directory is set correctly in `.env`

### 3. LLM returns empty or invalid payload

Check the configured GenAI model and ensure the model call is returning usable content. Also verify the prompt template remains valid JSON-structured output.

### 4. MongoDB or Qdrant connectivity issues

Confirm the connection strings and API keys are valid and that the services are reachable from the machine running the app.

## Future Improvements

Potential enhancements include:

- adding explicit API schemas for memory retrieval and creation
- supporting document deletion and re-indexing
- storing metadata such as source URLs and date ranges
- adding authentication and rate limiting
- adding a proper chat history abstraction instead of only session-based memory
- adding tests for ingestion, retrieval, and memory persistence

## License

This project does not currently declare a license file. Add a license if you plan to distribute it publicly or use it in production environments.

## Summary

`memory_augmented_rag` is a memory-aware document Q&A system that combines retrieval augmentation, semantic memory, and persistent user context to improve answer quality over time. It is most useful when a system needs to answer questions grounded in domain documents while remembering important user-specific context across sessions.
