# provider_loader.py
import os
import logging
from typing import Tuple, List, Any, Dict

from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore


# --- Configure logging ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)


# --- LLM + Embedding Initialization ---
def get_llm_and_embeddings(config: Dict) -> Tuple[Any, Any]:
    """
    Initializes and returns LLM and Embedding models based on configuration.

    Args:
        config (dict): Configuration dictionary, e.g.:
            {
                "llm": {"provider": "gemini", "model": "gemini-pro"},
                "embeddings": {"provider": "ollama", "model": "nomic-embed-text:latest"}
            }

    Returns:
        tuple: (llm, embeddings)
    """

    # LLM provider mapping
    llm_providers = {
        "ollama": lambda model: Ollama(model=model),
        "openai": lambda model: ChatOpenAI(
            model=model,
            openai_api_key=os.environ.get("OPENAI_API_KEY") # pyright: ignore[reportCallIssue]
        ),
        "gemini": lambda model: ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.environ.get("GOOGLE_API_KEY")
        ),
    }

    # Embedding provider mapping
    embedding_providers = {
        "ollama": lambda model: OllamaEmbeddings(model=model),
        "openai": lambda model: OpenAIEmbeddings(
            model=model,
            openai_api_key=os.environ.get("OPENAI_API_KEY") # type: ignore
        ),
        "gemini": lambda model: GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=os.environ.get("GOOGLE_API_KEY") # type: ignore
        ),
    }

    # --- Validate configuration ---
    llm_config = config.get("llm", {})
    embeddings_config = config.get("embeddings", {})

    if "provider" not in llm_config or "model" not in llm_config:
        raise ValueError("Missing or invalid LLM config: must include 'provider' and 'model'.")

    if "provider" not in embeddings_config or "model" not in embeddings_config:
        raise ValueError("Missing or invalid embeddings config: must include 'provider' and 'model'.")

    llm_provider = llm_config["provider"].lower()
    embedding_provider = embeddings_config["provider"].lower()

    if llm_provider not in llm_providers:
        raise ValueError(f"Unsupported LLM provider '{llm_provider}'. Available: {list(llm_providers.keys())}")

    if embedding_provider not in embedding_providers:
        raise ValueError(f"Unsupported embedding provider '{embedding_provider}'. Available: {list(embedding_providers.keys())}")

    # --- Initialize models ---
    llm = llm_providers[llm_provider](llm_config["model"])
    raw_embeddings = embedding_providers[embedding_provider](embeddings_config["model"])

    # --- Add local cache layer for embeddings ---
    cache_dir = config.get("embedding_cache_dir", "./cache/embeddings")
    os.makedirs(cache_dir, exist_ok=True)
    cache_store = LocalFileStore(cache_dir)
    embeddings = CacheBackedEmbeddings.from_bytes_store(raw_embeddings, cache_store)

    logging.info(f"✅ Loaded LLM: {llm_provider}/{llm_config['model']} | Embeddings: {embedding_provider}/{embeddings_config['model']}")
    return llm, embeddings


# --- Vector Store Loader ---
def get_vector_store(config: Dict, texts: List[Any], embeddings: Any) -> Any:
    """
    Creates or loads a vector store based on configuration.

    Args:
        config (dict): Configuration dict containing vector store settings.
        texts (List[Document]): LangChain documents to be embedded.
        embeddings: Embedding model used to encode documents.

    Returns:
        VectorStore: A LangChain-compatible vector store instance.
    """
    store_name = config.get("active_vector_store", "chroma").lower()

    if store_name == "chroma":
        persist_dir = config.get("persist_directory", "./chroma_store")
        os.makedirs(persist_dir, exist_ok=True)

        db_path = os.path.join(persist_dir, "chroma.sqlite3")

        # Check for existing DB to reuse
        if os.path.exists(db_path):
            logging.info("🔄 Found existing Chroma store. Loading from disk...")
            return Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings,
                collection_name=config.get("collection_name", "my_documents")
            )
        else:
            logging.info("🆕 Creating new Chroma vector store...")
            return Chroma.from_documents(
                documents=texts,
                embedding=embeddings,
                persist_directory=persist_dir,
                collection_name=config.get("collection_name", "my_documents")
            )

    # Uncomment and extend when ready
    # elif store_name == "pinecone":
    #     ...
    # elif store_name == "weaviate":
    #     ...
    else:
        raise ValueError(f"Vector store '{store_name}' not supported. Use 'chroma' (default).")
