# 1-rag

Sistema RAG sencillo usando PDFs, embeddings locales y una base vectorial Chroma.

El flujo sigue cuatro etapas:

1. Ingestion: lee el texto de un PDF.
2. Chunking: divide el texto en fragmentos de 1500 caracteres con overlap de 300.
3. Indexacion: convierte cada chunk en embeddings y los guarda en ChromaDB.
4. Recuperacion + generacion: busca contexto similar y lo inyecta en el prompt del LLM.

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Para generar respuestas con OpenAI, completa `OPENAI_API_KEY` en `.env`.
Si no hay API key, el script devuelve el contexto recuperado para validar el retrieval.

## Uso

Coloca un PDF en `data/` y ejecuta:

```bash
python rag_chroma.py index data/mi-documento.pdf
python rag_chroma.py ask "Que explica el documento sobre la etapa de ingestion?"
```

Tambien se puede indicar otra base o coleccion:

```bash
python rag_chroma.py index data/mi-documento.pdf --db-path chroma_db --collection workshop_rag
python rag_chroma.py ask "Como funciona la recuperacion?" --top-k 4
```

