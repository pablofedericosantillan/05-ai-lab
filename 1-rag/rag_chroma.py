from __future__ import annotations

import argparse
import os
import textwrap
import uuid
from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from pypdf import PdfReader


DEFAULT_COLLECTION = "rag_documents"
DEFAULT_DB_PATH = "chroma_db"
DEFAULT_CHUNK_SIZE = 1500
DEFAULT_CHUNK_OVERLAP = 300


@dataclass
class RetrievedChunk:
    text: str
    source: str
    page: int
    distance: float


def load_pdf(pdf_path: str | Path) -> list[dict]:
    """Extract raw text page by page from a PDF."""
    path = Path(pdf_path)
    reader = PdfReader(path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = normalize_text(text)
        if text:
            pages.append(
                {
                    "text": text,
                    "source": path.name,
                    "page": page_number,
                }
            )

    return pages


def normalize_text(text: str) -> str:
    """Compact whitespace so embeddings receive clean, stable input."""
    return " ".join(text.split())


def split_text(
    pages: list[dict],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict]:
    """Split PDF text into overlapping chunks while preserving source metadata."""
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[dict] = []
    step = chunk_size - chunk_overlap

    for page in pages:
        text = page["text"]
        for start in range(0, len(text), step):
            chunk_text = text[start : start + chunk_size].strip()
            if not chunk_text:
                continue

            chunks.append(
                {
                    "id": str(uuid.uuid4()),
                    "text": chunk_text,
                    "source": page["source"],
                    "page": page["page"],
                }
            )

            if start + chunk_size >= len(text):
                break

    return chunks


def get_embedding_function():
    """Use a local sentence-transformer model for embeddings."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )


def get_collection(
    db_path: str | Path = DEFAULT_DB_PATH,
    collection_name: str = DEFAULT_COLLECTION,
) -> Collection:
    """Create or load a persistent Chroma collection."""
    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=get_embedding_function(),
        metadata={"description": "Simple PDF RAG collection"},
    )


def index_pdf(
    pdf_path: str | Path,
    db_path: str | Path = DEFAULT_DB_PATH,
    collection_name: str = DEFAULT_COLLECTION,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> int:
    """Load, chunk, embed and store a PDF in ChromaDB."""
    pages = load_pdf(pdf_path)
    chunks = split_text(pages, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    if not chunks:
        raise ValueError(f"No text chunks were extracted from {pdf_path}")

    collection = get_collection(db_path=db_path, collection_name=collection_name)
    collection.add(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["text"] for chunk in chunks],
        metadatas=[
            {"source": chunk["source"], "page": chunk["page"]} for chunk in chunks
        ],
    )

    return len(chunks)


def retrieve_context(
    question: str,
    db_path: str | Path = DEFAULT_DB_PATH,
    collection_name: str = DEFAULT_COLLECTION,
    top_k: int = 4,
) -> list[RetrievedChunk]:
    """Search Chroma for chunks that are semantically similar to the question."""
    collection = get_collection(db_path=db_path, collection_name=collection_name)
    results = collection.query(query_texts=[question], n_results=top_k)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        retrieved.append(
            RetrievedChunk(
                text=document,
                source=str(metadata.get("source", "unknown")),
                page=int(metadata.get("page", 0)),
                distance=float(distance),
            )
        )

    return retrieved


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Inject retrieved context into a prompt for grounded generation."""
    context = "\n\n".join(
        f"[{index}] Fuente: {chunk.source}, pagina {chunk.page}\n{chunk.text}"
        for index, chunk in enumerate(chunks, start=1)
    )

    return f"""
    Responde la pregunta usando solo el contexto provisto.
    Si la respuesta no esta en el contexto, dilo claramente.

    Contexto:
    {context}

    Pregunta:
    {question}
    """.strip()


def generate_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    """Generate an answer with OpenAI, or return retrieved context if no key exists."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return format_retrieved_context(chunks)

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    prompt = build_prompt(question, chunks)

    response = client.responses.create(
        model=model,
        input=prompt,
    )
    return response.output_text


def ask_question(
    question: str,
    db_path: str | Path = DEFAULT_DB_PATH,
    collection_name: str = DEFAULT_COLLECTION,
    top_k: int = 4,
) -> str:
    """Run retrieval and answer generation as a single RAG query."""
    chunks = retrieve_context(
        question=question,
        db_path=db_path,
        collection_name=collection_name,
        top_k=top_k,
    )

    if not chunks:
        return "No se encontro contexto relevante en la base vectorial."

    return generate_answer(question, chunks)


def format_retrieved_context(chunks: list[RetrievedChunk]) -> str:
    """Show retrieved chunks when generation is disabled."""
    lines = [
        "OPENAI_API_KEY no esta configurada. Contexto recuperado:",
        "",
    ]

    for index, chunk in enumerate(chunks, start=1):
        preview = textwrap.shorten(chunk.text, width=700, placeholder="...")
        lines.append(
            f"[{index}] {chunk.source} pagina {chunk.page} "
            f"(distance={chunk.distance:.4f})\n{preview}\n"
        )

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple RAG pipeline with ChromaDB")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Index a PDF into ChromaDB")
    index_parser.add_argument("pdf_path", help="Path to the PDF file")
    index_parser.add_argument("--db-path", default=DEFAULT_DB_PATH)
    index_parser.add_argument("--collection", default=DEFAULT_COLLECTION)
    index_parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    index_parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)

    ask_parser = subparsers.add_parser("ask", help="Ask a question to the RAG system")
    ask_parser.add_argument("question", help="Question to answer")
    ask_parser.add_argument("--db-path", default=DEFAULT_DB_PATH)
    ask_parser.add_argument("--collection", default=DEFAULT_COLLECTION)
    ask_parser.add_argument("--top-k", type=int, default=4)

    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "index":
        total = index_pdf(
            pdf_path=args.pdf_path,
            db_path=args.db_path,
            collection_name=args.collection,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
        print(f"PDF indexado correctamente: {total} chunks guardados.")
        return

    if args.command == "ask":
        answer = ask_question(
            question=args.question,
            db_path=args.db_path,
            collection_name=args.collection,
            top_k=args.top_k,
        )
        print(answer)


if __name__ == "__main__":
    main()
