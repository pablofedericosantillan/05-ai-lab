import sys
from shared.config import (
    PDF_PATH,
)
from rag_services import (
    load_and_split_pdf,
    create_index_vector,
    retrieve_context,
    generate_answer,
)

def main() -> None:
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else PDF_PATH

    chunks = load_and_split_pdf(pdf_path)
    vector_store = create_index_vector(chunks)

    print("\nRAG system ready. Ask your question in Spanish (or 'exit' to quit).\n")

    while True:
        question = input("Question: ").strip()
        if question.lower() in {"salir", "exit", "quit"}:
            break
        if not question:
            continue

        retrieved = retrieve_context(question, vector_store)
        answer = generate_answer(question, retrieved)
        print(f"\nAnswer: {answer}\n")


if __name__ == "__main__":
    main()
