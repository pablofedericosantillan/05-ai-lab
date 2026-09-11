import os
from pathlib import Path
import shutil
from langchain_core.documents import Document

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_text_splitters import RecursiveCharacterTextSplitter

from shared.constants import SYSTEM_PROMPT
from shared.config import (
    PDF_PATH,
    CHROMA_DIR,
    EMBEDDING_MODEL,
    HF_MODEL_ID,
    HUGGINGFACEHUB_API_TOKEN,
    LANGSMITH_TRACING,
    LANGSMITH_API_KEY,
    LANGSMITH_ENDPOINT,
)

########################################################
# STEP-1: load and split document 
########################################################
def load_and_split_pdf(pdf_path: str | Path, chunk_size: int=1500, chunk_overlap:int=300) -> list[Document]:
    print("Step-1: load and split document. . . .\n")

    path = Path(pdf_path)
    loader = PyPDFLoader(path)
    pages=loader.load()

    splitter= RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks=splitter.split_documents(pages)

    return chunks


########################################################
# STEP-2: indexation - vector store
########################################################
def create_index_vector(
    chunks: list[Document],
):
    """
    First, we clean the old data base, and convert the chunks to vector and save in the chroma-db
    """
    print("Step-2: Generating embeddings and creating a vector index. . . .\n")

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


########################################################
# STEP-3: retrieval
########################################################
def retrieve_context(
    question: str,
    vector_store: Chroma,
    top_k: int = 5,
):
    print("Step-3: Search and retrieve info. . . .\n",)
    retrieval_docs = vector_store.similarity_search(question, k=top_k)

    return retrieval_docs

########################################################
# STEP-4: Response generation (LLM + Prompt)
########################################################
def generate_answer(question: str, chunks: list[Document]) -> str:
    print("Step-4: Respond generation with LLM. . . .\n")

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
