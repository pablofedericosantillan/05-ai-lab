import os
from pathlib import Path
import shutil
import sys
from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_text_splitters import RecursiveCharacterTextSplitter

################################################################################################################


########################################################
# Global variables and basic configuration
########################################################
PDF_PATH = os.getenv("PDF_PATH", "data/mi-documento.pdf")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db_pdf")

EMBEDDING_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "Qwen/Qwen3.5-4B")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "rag-pdf-demo")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")


SYSTEM_PROMPT = """
Sos un asistente de IA experto en analisis de documentos. Tu unico objetivo es responder las preguntas del usuario basado EXCLUSIVAMENTE en el documento proporcionado.

REGLAS ESTRICTAS:
1- IDIOMA: responde en español, de forma natural y directa. NO incluyas traducciones ni texto en otro idioma.
2- CERO ALUCINACIONES: si la respuesta no se encuentra en el contexto, no intentes adivinarla ni uses conocimiento previo. Responde EXACTAMENTE: "No encuentro suficiente informacion".
3- CERO RAZONAMIENTO: entrega directamente la respuesta final. Esta estrictamente prohibido usar frases introductorias como "Pensando...", "Segun el contexto..."
4- CITAS OBLIGATORIAS: siempre que el contexto lo permita, inclui la referencia al final de tu respuesta usando el formato [pag. X, seccion Y].

EJEMPLO DE RESPUESTA ESPERADA:
La familia de Ana se esconde en el anexo secreto del edificio donde trabajaba su padre, ubicado en Amsterdam [pag. 12, seccion 9 de julio de 1942].
"""

################################################################################################################

########################################################
# STEP-1: load and split document 
########################################################
def load_and_split_pdf(pdf_path: str | Path, chunk_size: int=1500, chunk_overlap:int=300) -> list[Document]:
    print("Step-1: load and split document. . . .")

    path = Path(pdf_path)
    loader = PyPDFLoader(path)
    pages=loader.load()

    splitter= RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks=splitter.split_documents(pages)

    return chunks


################################################################################################################

########################################################
# STEP-2: indexation - vector store
########################################################

def create_index_vector(
    chunks: list[Document],
):
    """
    First, we clean the old data base, and convert the chunks to vector and save in the chroma-db
    """
    print("Step-2: Generating embeddings and creating a vector index. . . .")

    if os.path.exists(CHROMA_DIR):
        print("Step-2: ->> Cleaning data base. . . .")
        shutil.rmtree(CHROMA_DIR)

    embeddings = HuggingFaceEmbeddings(model=EMBEDDING_MODEL)

    vector_store=Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    return vector_store


################################################################################################################

########################################################
# STEP-3: retrieval
########################################################
def retrieve_context(
    question: str,
    vector_store: Chroma,
    top_k: int = 5,
):
    print("Step-3: Search and retrive information. . . .")
    retrieval_docs = vector_store.similarity_search(question, k=top_k)

    return retrieval_docs


################################################################################################################

########################################################
# STEP-4: Response generation (LLM + Prompt)
########################################################
def generate_answer(question: str, chunks: list[Document]) -> str:
    print("Step-4: Responde generation with LLM. . . .")

    model_base=HuggingFaceEndpoint(
        repo_id=HF_MODEL_ID,
        max_new_tokens=256,
        temperature=0.1,
    )

    llm = ChatHuggingFace(llm=model_base)

    context="\n\n".join([doc.page_content for doc in chunks])

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context}\n\nQuery:\n{question}")
    ]

    output=llm.invoke(messages)
    return output.content




def main() -> None:
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else PDF_PATH

    chunks = load_and_split_pdf(pdf_path)
    vector_store = create_index_vector(chunks)

    print("\nSistema RAG listo. Escribi tu pregunta (o 'salir' para terminar).\n")

    while True:
        question = input("Pregunta: ").strip()
        if question.lower() in {"salir", "exit", "quit"}:
            break
        if not question:
            continue

        retrieved = retrieve_context(question, vector_store)
        answer = generate_answer(question, retrieved)
        print(f"\nRespuesta: {answer}\n")


if __name__ == "__main__":
    main()
