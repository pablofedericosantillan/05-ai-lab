# 1-rag

Simple RAG system using PDFs, local embeddings (Hugging Face), and a Chroma vector store.

The flow follows four stages:

1. Ingestion: reads the text from a PDF (`PyPDFLoader`).
2. Chunking: splits the text into 1500-character fragments with 300-character overlap.
3. Indexing: converts each chunk into embeddings and stores them in ChromaDB.
4. Retrieval + generation: searches for similar context and injects it into the prompt of an LLM served by Hugging Face.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your variables:

- `PDF_PATH`: default path of the PDF to index.
- `CHROMA_DIR`: folder where the vector store is persisted.
- `EMBEDDING_MODEL`: `sentence-transformers` model used for the embeddings.
- `HUGGINGFACEHUB_API_TOKEN` and `HF_MODEL_ID`: Hugging Face credential and model used to generate the answers.
- `LANGSMITH_*` (optional): tracing for the LLM calls.

## Usage

Place a PDF in `data/` (or point `PDF_PATH` to its location) and run:

```bash
python main.py data/mi-documento.pdf
```

If you don't pass a path, it uses the `PDF_PATH` defined in `.env`. On startup it indexes the PDF into Chroma and then opens an interactive prompt for asking questions:

```
Sistema RAG listo. Escribi tu pregunta (o 'salir' para terminar).

Pregunta: Que explica el documento sobre la etapa de ingestion?

Respuesta: ...

Pregunta: salir
```
