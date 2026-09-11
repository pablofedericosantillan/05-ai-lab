import os
from dotenv import load_dotenv

load_dotenv()

########################################################
# Global variables and basic configuration
########################################################
PDF_PATH = os.getenv("PDF_PATH", "data/source.pdf")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db_pdf")

EMBEDDING_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "Qwen/Qwen3.5-4B")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "rag-pdf-demo")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")