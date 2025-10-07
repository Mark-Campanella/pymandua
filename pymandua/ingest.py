# ingest.py
import os
import yaml
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .provider_loader import get_llm_and_embeddings, get_vector_store


# ---------- Logging Setup ----------
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------- Config Loader ----------
def load_config(file_path: str):
    """Loads configuration from a YAML file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found at: {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


# ---------- Parallel File Loader ----------
def load_files_concurrently(source_directory: str, extensions: list[str], max_workers: int = 8):
    """
    Loads files concurrently using ThreadPoolExecutor with a progress bar.
    """
    documents = []
    file_paths = [
        os.path.join(root, file)
        for root, _, files in os.walk(source_directory)
        for file in files if any(file.endswith(ext) for ext in extensions)
    ]

    if not file_paths:
        return []

    logger.info(f"Discovered {len(file_paths)} markdown files. Loading in parallel...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(TextLoader(path, encoding='utf-8', autodetect_encoding=True).load): path
            for path in file_paths
        }
        for future in tqdm(as_completed(futures), total=len(futures), desc="Loading files", ncols=80):
            try:
                documents.extend(future.result())
            except Exception as e:
                logger.warning(f"Failed to load {futures[future]}: {e}")

    return documents


# ---------- Ingestion Pipeline ----------
def ingest_data(config: dict):
    """
    Loads, splits, and embeds documents based on a given configuration.
    """

    required_keys = [
        "source_directory", "persist_directory",
        "chunking", "llm", "embeddings", "active_vector_store"
    ]
    missing = [k for k in required_keys if k not in config]
    if missing:
        raise KeyError(f"Missing configuration keys: {missing}")

    source_directory = config["source_directory"]
    persist_directory = config["persist_directory"]
    chunk_size = config["chunking"]["chunk_size"]
    chunk_overlap = config["chunking"]["chunk_overlap"]

    logger.info(f"--- INGESTING MARKDOWN CONTENT ---")
    logger.info(f"Processing files from: {source_directory}")
    logger.info(f"Storing in: {persist_directory}")

    if os.path.exists(persist_directory):
        logger.warning(f"Vector store already exists at '{persist_directory}'.")
        choice = input("Overwrite existing data? (y/n): ").strip().lower()
        if choice != "y":
            logger.info("Ingestion cancelled by user.")
            return

    # Load Markdown files concurrently
    documents = load_files_concurrently(source_directory, [".md", ".markdown", ".mkd", ".mdown"])
    if not documents:
        logger.warning("No Markdown files found. Nothing to ingest.")
        return

    logger.info(f"Total documents loaded: {len(documents)}")

    # Split text into chunks with progress tracking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    texts = []
    for doc in tqdm(documents, desc="Splitting documents", ncols=80):
        chunks = text_splitter.split_documents([doc])
        texts.extend(chunk for chunk in chunks if chunk.page_content.strip())

    logger.info(f"Total chunks generated: {len(texts)}")

    llm_and_embeddings_config = {
        "llm": config["llm"],
        "embeddings": config["embeddings"]
    }
    _, embeddings = get_llm_and_embeddings(llm_and_embeddings_config)

    vectordb = get_vector_store(config, texts, embeddings)

    if hasattr(vectordb, "persist"):
        vectordb.persist()
        logger.info(f"Vector store persisted successfully at: {persist_directory}")

    vector_store_provider = config["active_vector_store"]
    logger.info(f"Ingestion completed using provider: {vector_store_provider}")


# ---------- CLI Entry ----------
if __name__ == "__main__":
    try:
        config_path = "config.yaml"
        cfg = load_config(config_path)
        ingest_data(cfg)
    except Exception as e:
        logger.exception(f"Ingestion failed: {e}")

