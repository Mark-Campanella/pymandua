# ingest.py
import yaml
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Assuming these are your custom modules
from provider_loader import get_llm_and_embeddings, get_vector_store

def load_config(file_path: str):
    """Loads configuration from a YAML file."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def ingest_data(config: dict):
    """
    Loads, splits, and embeds documents based on a given configuration.
    """
    source_directory = config["source_directory"]
    persist_directory = config["persist_directory"]
    chunk_size = config["chunking"]["chunk_size"]
    chunk_overlap = config["chunking"]["chunk_overlap"]

    print(f"--- INGESTING MARKDOWN CONTENT ---")
    print(f"Processing files from: {source_directory}")
    print(f"Storing in: {persist_directory}")

    try:
        loader = DirectoryLoader(source_directory, glob="*.md", loader_cls=TextLoader)
        documents = loader.load()
        if not documents:
            print("No Markdown files found.")
            return

        print(f"Total documents loaded: {len(documents)}")
    except FileNotFoundError:
        print(f"Error: The source directory '{source_directory}' was not found.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    print(f"Total chunks generated: {len(texts)}")

    # We only need the embeddings for this step. We must pass a correctly
    # formatted config dictionary to get_llm_and_embeddings.
    embeddings_config = config["embeddings"]
    # The LLM config is not needed, so we can pass an empty dictionary for it.
    llm_and_embeddings_config = {"llm": {}, "embeddings": embeddings_config}

    _, embeddings = get_llm_and_embeddings(llm_and_embeddings_config)

    vectordb = get_vector_store(config, texts, embeddings)
    
    # It's better to get the vector store provider from the new config structure
    vector_store_provider = config["active_vector_store"]
    print(f"Ingestion completed. Using {vector_store_provider} as vector store.")

if __name__ == "__main__":
    # To maintain its standalone functionality, we define the path here.
    config_path = "config.yaml"
    cfg = load_config(config_path)
    ingest_data(cfg)