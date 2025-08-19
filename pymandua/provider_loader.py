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
    provider = config["active_provider"]
    provider_config = config[provider]
    
    providers_map = {
        "ollama": {
            "llm": Ollama(model=provider_config["llm_model"]),
            "embeddings": OllamaEmbeddings(model=provider_config["embedding_model"])
        },
        "openai": {
            "llm": ChatOpenAI(
                model=provider_config["llm_model"],
                openai_api_key=os.environ.get("OPENAI_API_KEY")
            ),
            "embeddings": OpenAIEmbeddings(
                model=provider_config["embedding_model"],
                openai_api_key=os.environ.get("OPENAI_API_KEY")
            )
        },
        "gemini": {
            "llm": ChatGoogleGenerativeAI(
                model=provider_config["llm_model"],
                google_api_key=os.environ.get("GEMINI_API_KEY")
            ),
            "embeddings": GoogleGenerativeAIEmbeddings(
                model=provider_config["embedding_model"],
                google_api_key=os.environ.get("GEMINI_API_KEY")
            )
        }
    }

    if provider not in providers_map:
        raise ValueError(f"Provedor '{provider}' não suportado. Escolha entre {list(providers_map.keys())}.")
    
    return providers_map[provider]["llm"], providers_map[provider]["embeddings"]


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