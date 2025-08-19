# query.py
import yaml
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from provider_loader import get_llm_and_embeddings

def load_config(file_path="config.yaml"):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def get_answer(question: str):
    config = load_config()
    persist_directory = config["persist_directory"]

    print("Conectando ao banco de dados e ao modelo...")
    
    llm, embeddings = get_llm_and_embeddings(config)

    if config["active_vector_store"] == "chroma":
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    else:
        raise NotImplementedError("A lógica de carregamento para este banco de dados não foi implementada na consulta.")

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(),
        return_source_documents=True
    )
    
    print(f"Buscando a resposta para a pergunta: '{question}'")
    
    result = qa_chain({"query": question})
    
    print("\n--- RESPOSTA ---")
    print(result['result'])
    print("\n--- FONTES ---")
    for doc in result['source_documents']:
        print(f"Fonte: {doc.metadata.get('source', 'Não especificado')}")
        print(f"Conteúdo: {doc.page_content[:150]}...")
        print("-" * 20)

if __name__ == "__main__":
    while True:
        user_question = input("\nFaça sua pergunta (ou digite 'sair' para encerrar): ")
        if user_question.lower() == 'sair':
            break
        try:
            get_answer(user_question)
        except Exception as e:
            print(f"Ocorreu um erro: {e}")