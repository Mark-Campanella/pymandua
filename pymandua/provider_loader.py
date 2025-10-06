# provider_loader.py

import os
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
# from langchain_community.vectorstores import Pinecone
# from langchain_community.vectorstores import Weaviate
# import pinecone
# import weaviate

def get_llm_and_embeddings(config):
    """
    Initializes and returns LLM and Embedding models based on a flexible configuration.

    Args:
        config (dict): A configuration dictionary with separate 'llm' and 'embeddings'
                       sections, each specifying its own provider and model.
                       Example:
                       {
                           "llm": {"provider": "gemini", "model": "gemini-pro"},
                           "embeddings": {"provider": "ollama", "model": "nomic-embed-text:latest"}
                       }
    Returns:
        tuple: A tuple containing the initialized LLM and Embeddings objects.
    """
    # Define a mapping for LLM providers
    llm_providers = {
        "ollama": lambda model: Ollama(model=model),
        "openai": lambda model: ChatOpenAI(
            model=model,
            openai_api_key=os.environ.get("OPENAI_API_KEY") # pyright: ignore[reportCallIssue]
        ),
        "gemini": lambda model: ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.environ.get("GOOGLE_API_KEY") # Corrected variable name for clarity
        )
    }

    # Define a mapping for Embedding providers
    embedding_providers = {
        "ollama": lambda model: OllamaEmbeddings(model=model),
        "openai": lambda model: OpenAIEmbeddings(
            model=model,
            openai_api_key=os.environ.get("OPENAI_API_KEY") # type: ignore
        ),
        "gemini": lambda model: GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=os.environ.get("GOOGLE_API_KEY") # pyright: ignore[reportArgumentType]
        )
    }

    # Retrieve LLM configuration
    llm_config = config.get("llm")
    if not llm_config or "provider" not in llm_config or "model" not in llm_config:
        raise ValueError("LLM configuration is missing or malformed. Please specify 'provider' and 'model'.")
    
    llm_provider_name = llm_config["provider"]
    llm_model_name = llm_config["model"]
    
    # Retrieve Embeddings configuration
    embeddings_config = config.get("embeddings")
    if not embeddings_config or "provider" not in embeddings_config or "model" not in embeddings_config:
        raise ValueError("Embeddings configuration is missing or malformed. Please specify 'provider' and 'model'.")

    embedding_provider_name = embeddings_config["provider"]
    embedding_model_name = embeddings_config["model"]

    # Validate and get LLM instance
    if llm_provider_name not in llm_providers:
        raise ValueError(f"LLM provider '{llm_provider_name}' is not supported. Choose from {list(llm_providers.keys())}.")
    
    llm = llm_providers[llm_provider_name](llm_model_name)

    # Validate and get Embeddings instance
    if embedding_provider_name not in embedding_providers:
        raise ValueError(f"Embedding provider '{embedding_provider_name}' is not supported. Choose from {list(embedding_providers.keys())}.")
    
    embeddings = embedding_providers[embedding_provider_name](embedding_model_name)

    return llm, embeddings

def get_vector_store(config, texts, embeddings):
    """
    Cria e retorna a instância do banco de dados vetorial com base na configuração.
    """
    store_name = config["active_vector_store"]
    
    if store_name == "chroma":
        # ChromaDB é um banco de dados local
        persist_dir = config["persist_directory"]
        return Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=persist_dir
        )
    # elif store_name == "pinecone":
    #     pinecone.init(
    #         api_key=os.environ.get(config["pinecone"]["api_key_env_var"]),
    #         environment=os.environ.get(config["pinecone"]["environment_env_var"])
    #     )
    #     index_name = config["pinecone"]["index_name"]
    #     if index_name not in pinecone.list_indexes():
    #         # Cria o índice se ele não existir
    #         pinecone.create_index(name=index_name, dimension=embeddings.client.model.dimension)
    #     return Pinecone.from_documents(texts, embeddings, index_name=index_name)
    # elif store_name == "weaviate":
    #     auth_config = weaviate.AuthApiKey(api_key=os.environ.get(config["weaviate"]["api_key_env_var"]))
    #     client = weaviate.Client(
    #         url=config["weaviate"]["url"],
    #         auth_client_secret=auth_config,
    #         additional_headers={"X-OpenAI-Api-Key": os.environ.get("OPENAI_API_KEY")}
    #     )
    #     return Weaviate.from_documents(
    #         texts, embeddings, client=client, index_name=config["weaviate"]["index_name"]
    #     )
    else:
        raise ValueError(f"Banco de dados vetorial '{store_name}' não suportado. Escolha entre 'chroma', 'pinecone', 'weaviate'.")