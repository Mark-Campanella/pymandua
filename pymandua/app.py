# app.py

import yaml
import gradio as gr
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from provider_loader import get_llm_and_embeddings

# This function now takes 'config' as an argument
def setup_qa_chain(config: dict):
    persist_directory = config["persist_directory"]
    
    llm, embeddings = get_llm_and_embeddings(config)
    
    if config["active_vector_store"] == "chroma":
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    else:
        raise NotImplementedError("The loading logic for this vector store has not been implemented in the query app.")
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(),
        return_source_documents=True
    )
    return qa_chain

# Global chain for the Gradio app
def launch_app(config: dict):
    # This function will now initialize the chain with the passed config
    qa_chain = setup_qa_chain(config)
    
    # Use a lambda function to pass the chain to the response functions
    def simple_qa_with_chain(query: str):
        if not query: return "Please enter a query."
        result = qa_chain({"query": query})
        return result['result']

    def generate_table_with_chain(query: str, headers: str):
        if not query or not headers: return "Please enter a query and headers."
        headers_list = [h.strip() for h in headers.split(',')]
        result = qa_chain({"query": query})
        context = " ".join([doc.page_content for doc in result['source_documents']])
        
        prompt = f"""
        You are a data extraction assistant. Your task is to extract information from the provided context and present it in a structured table.
        Use the following headers for the table. If a piece of information is not found in the context for a column, fill with 'N/A'.

        Context:
        {context}

        User query: {query}
        
        Table Headers: {', '.join(headers_list)}

        Please provide the response strictly in Markdown table format, using the requested headers.
        """
        
        llm = qa_chain.llm
        table_output = llm.invoke(prompt)
        return table_output

    with gr.Blocks() as demo:
        # ... (Gradio layout code) ...
        with gr.Tabs():
            with gr.TabItem("Simple Q&A"):
                qa_query_input = gr.Textbox(label="Your Query")
                qa_answer_output = gr.Markdown(label="Response")
                qa_submit_btn = gr.Button("Get Response")
            with gr.TabItem("Table Generator"):
                table_query_input = gr.Textbox(label="Your Query")
                table_headers_input = gr.Textbox(
                    label="Headers for Table (comma-separated)",
                    placeholder="Ex: Name, Position, Department"
                )
                table_output = gr.Markdown(label="Table")
                table_submit_btn = gr.Button("Generate Table")

        qa_submit_btn.click(fn=simple_qa_with_chain, inputs=qa_query_input, outputs=qa_answer_output)
        table_submit_btn.click(fn=generate_table_with_chain, inputs=[table_query_input, table_headers_input], outputs=table_output)
        
    demo.launch(inbrowser=True)