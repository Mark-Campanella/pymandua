# query.py
import yaml
import logging
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from .provider_loader import get_llm_and_embeddings


# ---------- Logging Setup ----------
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------- Config Loader ----------
def load_config(file_path="config.yaml"):
    if not file_path:
        raise ValueError("Config path cannot be empty.")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at: {file_path}")
        raise


# ---------- QA Function ----------
def get_answer(question: str):
    if not question.strip():
        logger.warning("Empty question provided.")
        return

    config = load_config()
    persist_directory = config["persist_directory"]

    logger.info("Connecting to vector store and LLM...")

    llm, embeddings = get_llm_and_embeddings(config)

    if config["active_vector_store"] == "chroma":
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    else:
        raise NotImplementedError(
            f"Vector store '{config['active_vector_store']}' is not supported yet."
        )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(),
        return_source_documents=True
    )

    logger.info(f"Querying: '{question}'")

    try:
        result = qa_chain({"query": question})
    except Exception as e:
        logger.error(f"Failed to retrieve answer: {e}")
        return

    print("\n--- ANSWER ---")
    print(result.get("result", "No result found."))

    print("\n--- SOURCES ---")
    source_docs = result.get("source_documents", [])
    if not source_docs:
        print("No source documents returned.")
    for doc in source_docs:
        source = doc.metadata.get("source", "Unknown source")
        snippet = doc.page_content[:150].replace("\n", " ")
        print(f"Source: {source}\nSnippet: {snippet}...")
        print("-" * 20)


# ---------- CLI Entry ----------
if __name__ == "__main__":
    while True:
        user_question = input("\nEnter your question (or type 'exit' to quit): ").strip()
        if user_question.lower() in ["exit", "quit", "sair"]:
            logger.info("Session ended by user.")
            break
        try:
            get_answer(user_question)
        except Exception as e:
            logger.exception(f"An error occurred while processing the query: {e}")
