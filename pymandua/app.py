# app.py
import yaml
import gradio as gr
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
import chromadb
import re
from .provider_loader import get_llm_and_embeddings


# --- 1. SETUP FUNCTION WITH LCEL ---
def setup_qa_chain(config: dict):
    persist_directory = config["persist_directory"]

    # 1. Initialize LLM and embeddings
    llm, embeddings = get_llm_and_embeddings(config)

    # 2. Load Vector Store
    if config["active_vector_store"] == "chroma":
        try:
            client = chromadb.PersistentClient(path=persist_directory)
            vectordb = Chroma(
                client=client,
                collection_name="my_documents",
                embedding_function=embeddings
            )
        except Exception:
            raise FileNotFoundError(
                f"ChromaDB not found at {persist_directory}. Please run ingestion first."
            )
    else:
        raise NotImplementedError("The loading logic for this vector store has not been implemented.")

    # 3. Create Retriever
    retriever = vectordb.as_retriever()

    # 4. Define RAG prompt
    rag_prompt = ChatPromptTemplate.from_template("""
        You are a helpful assistant. Use the following context to answer the question concisely.
        
        Context:
        {context}

        Question:
        {question}
        """)

    # 5. Build LCEL chain
    qa_chain = (
        {
            "context": retriever,
            "question": RunnableLambda(lambda x: x if isinstance(x, str) else x.get("question", str(x)))
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    return qa_chain, llm, retriever


# --- 2. RESPONSE FUNCTIONS ---
def launch_app(config: dict):
    qa_chain, llm, retriever = setup_qa_chain(config)

    def simple_qa_with_chain(query: str):
        if not query:
            return "Please enter a query."

        # Run RAG chain usando apenas a string
        response = qa_chain.invoke(query)  # <-- sem {"question": query}

        # Retrieve context for source display
        docs = retriever.invoke(query)
        sources = [doc.metadata.get("source", "Unknown") for doc in docs]
        source_text = "\n\n**Sources:**\n" + "\n".join(f"- {s}" for s in sources)

        return response + source_text


    def validate_table_markdown(text: str) -> str:
        """Ensures the model output is a valid Markdown table."""
        if re.search(r"^\|.*\|", text, re.MULTILINE):
            return text
        return "⚠️ The model did not return a valid table. Try rephrasing your query."

    def generate_table_with_chain(query: str, headers: str):
        if not query or not headers:
            return "Please enter a query and headers."

        headers_list = [h.strip() for h in headers.split(',') if h.strip()]
        if not headers_list:
            return "No valid headers provided."

        # Retrieve context
        docs = retriever.invoke(query)
        context = " ".join([doc.page_content for doc in docs])

        # Create structured extraction prompt
        prompt = f"""
        You are a data extraction assistant.
        Use the provided context to extract information and present it *only* as a Markdown table.

        If some data is missing, fill with 'N/A'.
        Do not add explanations before or after the table.

        Context:
        {context}

        User query:
        {query}

        Table Headers:
        {', '.join(headers_list)}
        """

        table_output = llm.invoke(prompt)
        return validate_table_markdown(table_output.content if hasattr(table_output, "content") else str(table_output))

    # --- 3. UI ---
    with gr.Blocks(theme="soft") as demo:
        gr.Markdown("# 🧠 RAG QA + Table Generator")

        with gr.Tabs():
            with gr.TabItem("Simple Q&A"):
                gr.Markdown("Ask a question about your ingested documents.")
                qa_query_input = gr.Textbox(label="Your Query", placeholder="Ex: What are the main findings?")
                qa_answer_output = gr.Markdown(label="Response")
                qa_submit_btn = gr.Button("Get Response", variant="primary")
                
                # Conectar botão à função
                qa_submit_btn.click(
                    fn=simple_qa_with_chain,         
                    inputs=qa_query_input,           
                    outputs=qa_answer_output       
                )

            with gr.TabItem("Table Generator"):
                gr.Markdown("Extract structured data from your context.")
                table_query_input = gr.Textbox(label="Your Query", placeholder="Ex: List all employees and roles")
                table_headers_input = gr.Textbox(
                    label="Headers (comma-separated)",
                    placeholder="Ex: Name, Position, Department"
                )
                table_output = gr.Markdown(label="Generated Table")
                table_submit_btn = gr.Button("Generate Table", variant="primary")

        qa_submit_btn.click(fn=simple_qa_with_chain, inputs=qa_query_input, outputs=qa_answer_output)
        table_submit_btn.click(fn=generate_table_with_chain, inputs=[table_query_input, table_headers_input], outputs=table_output)

    demo.launch(inbrowser=True)
