# ingest.py
import yaml
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from provider_loader import get_llm_and_embeddings, get_vector_store
def load_config(file_path="config.yaml"):
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

    _, embeddings = get_llm_and_embeddings(config)

    vectordb = get_vector_store(config, texts, embeddings)
    
    print(f"Ingestion completed. Using {config['active_vector_store']} as vector store.")

if __name__ == "__main__":
    # to maintain its standalone functionality.
    import yaml
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    ingest_data(cfg)
