# 1-rag

Simple RAG system using PDFs, local embeddings (Hugging Face), and a Chroma vector store.

The flow follows four stages:

1. Ingestion: reads the text from a PDF (`PyPDFLoader`).
2. Chunking: splits the text into 1500-character fragments with 300-character overlap.
3. Indexing: converts each chunk into embeddings and stores them in ChromaDB.
4. Retrieval + generation: searches for similar context and injects it into the prompt of an LLM served by Hugging Face.

## Installation

Run everything from this folder (`1-example_simple_rag/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:

- `PDF_PATH`: default PDF to index (default: `../data/source.pdf`).
- `CHROMA_DIR`: folder where the vector store is persisted.
- `EMBEDDING_MODEL`: `sentence-transformers` model used for the embeddings.
- `HUGGINGFACEHUB_API_TOKEN` and `HF_MODEL_ID`: Hugging Face credential and model used to generate the answers.
- `LANGSMITH_*` (optional): tracing for the LLM calls.

## Usage

```bash
python main.py                      # uses PDF_PATH from .env
python main.py ../data/source.pdf   # or pass a PDF explicitly
```

The first run downloads the embedding model and indexes the PDF (it rebuilds
`CHROMA_DIR` from scratch every time), then opens an interactive prompt:

```
RAG system ready. Ask your question in Spanish (or 'exit' to quit).

Question: Que explica el documento sobre la etapa de ingestion?

Answer: ...

Question: exit
```
