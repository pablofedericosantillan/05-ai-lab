# 1-rag

Sistema RAG sencillo usando PDFs, embeddings locales (Hugging Face) y una base vectorial Chroma.

El flujo sigue cuatro etapas:

1. Ingestion: lee el texto de un PDF (`PyPDFLoader`).
2. Chunking: divide el texto en fragmentos de 1500 caracteres con overlap de 300.
3. Indexacion: convierte cada chunk en embeddings y los guarda en ChromaDB.
4. Recuperacion + generacion: busca contexto similar y lo inyecta en el prompt de un LLM servido por Hugging Face.

## Instalacion

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Completa `.env` con tus variables:

- `PDF_PATH`: ruta por defecto del PDF a indexar.
- `CHROMA_DIR`: carpeta donde se persiste la base vectorial.
- `EMBEDDING_MODEL`: modelo de `sentence-transformers` usado para los embeddings.
- `HUGGINGFACEHUB_API_TOKEN` y `HF_MODEL_ID`: credencial y modelo de Hugging Face usados para generar las respuestas.
- `LANGSMITH_*` (opcional): tracing de las llamadas al LLM.

## Uso

Coloca un PDF en `data/` (o apunta `PDF_PATH` a su ubicacion) y ejecuta:

```bash
python main.py data/mi-documento.pdf
```

Si no pasas un path, usa el `PDF_PATH` definido en `.env`. Al arrancar, indexa el PDF en Chroma y despues abre un prompt interactivo para hacer preguntas:

```
Sistema RAG listo. Escribi tu pregunta (o 'salir' para terminar).

Pregunta: Que explica el documento sobre la etapa de ingestion?

Respuesta: ...

Pregunta: salir
```
