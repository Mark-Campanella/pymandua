# app.py
import os
import yaml
import gradio as gr
import json
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
import chromadb
import re
import csv
import io
from dotenv import load_dotenv
from .provider_loader import get_llm_and_embeddings
import tempfile

# --- SETUP FUNCTION ---
def setup_qa_chain(config: dict):
    persist_directory = config["persist_directory"]
    llm, embeddings = get_llm_and_embeddings(config)

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
        raise NotImplementedError("Only Chroma vector store is implemented.")

    retriever = vectordb.as_retriever()

    rag_prompt = ChatPromptTemplate.from_template("""
        You are a helpful assistant. Use the following context to answer the question concisely.

        Context:
        {context}

        Question:
        {question}
    """)

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
def log_to_file(output_file, data):
    """Append a record to a JSON file."""
    record = {
        "timestamp": datetime.now().isoformat(),
        **data
    }
    if not os.path.exists(output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([record], f, ensure_ascii=False, indent=4)
    else:
        with open(output_file, "r+", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []
            existing.append(record)
            f.seek(0)
            json.dump(existing, f, ensure_ascii=False, indent=4)

# --- APP FUNCTION ---
def launch_app(config_or_path="config.yaml"):
    load_dotenv()

    # Allow both dict or config path
    if isinstance(config_or_path, dict):
        default_config = config_or_path
    elif isinstance(config_or_path, (str, bytes, os.PathLike)):
        with open(config_or_path, "r", encoding="utf-8") as f:
            default_config = yaml.safe_load(f)
    else:
        raise TypeError("config_or_path must be either a dict or a path to a config file.")

    # --- Build dynamic chain ---
    def build_chain(llm_provider, llm_model, emb_provider, emb_model, api_key, persist_dir, output_file):
        """Rebuilds the QA chain with dynamic runtime configuration and updates environment variables."""
        if api_key:
            key_env_map = {
                "openai": "OPENAI_API_KEY",
                "gemini": "GOOGLE_API_KEY",
                "ollama": "OLLAMA_API_KEY"
            }
            env_var = key_env_map.get(llm_provider.lower())
            if env_var:
                os.environ[env_var] = api_key

        config = default_config.copy()
        config.update({
            "llm_provider": llm_provider,
            "llm_model": llm_model,
            "embedding_provider": emb_provider,
            "embedding_model": emb_model,
            "persist_directory": persist_dir,
            "output_file": output_file
        })

        return setup_qa_chain(config)

    # --- Main Functions ---
    def simple_qa_with_chain(query, llm_provider, llm_model, emb_provider, emb_model, api_key, persist_dir, output_file):
        if not query:
            return "Please enter a query."

        qa_chain, llm, retriever = build_chain(llm_provider, llm_model, emb_provider, emb_model, api_key, persist_dir, output_file)
        response = qa_chain.invoke(query)
        docs = retriever.invoke(query)
        sources = [doc.metadata.get("source", "Unknown") for doc in docs]
        source_text = "\n\n**Sources:**\n" + "\n".join(f"- {s}" for s in sources)
        full_response = response + source_text
        if output_file:
            log_to_file(output_file, {"type": "Q&A", "query": query, "response": full_response})


        return full_response

    def generate_table_with_chain(query, headers, llm_provider, llm_model, emb_provider, emb_model, api_key, persist_dir, output_file):
        if not query or not headers:
            return "Please enter a query and headers."

        qa_chain, llm, retriever = build_chain(llm_provider, llm_model, emb_provider, emb_model, api_key, persist_dir, output_file)
        docs = retriever.invoke(query)
        context = " ".join([doc.page_content for doc in docs])
        headers_list = [h.strip() for h in headers.split(',') if h.strip()]

        prompt = f"""
        You are a data extraction assistant.
        Use the provided context to extract information and present it *only* as a Markdown table.

        If some data is missing, fill it with 'N/A'.
        Do not add explanations before or after the table.

        Context:
        {context}

        User Query:
        {query}

        Table Headers:
        {', '.join(headers_list)}
        """

        table_output = llm.invoke(prompt)
        text = table_output.content if hasattr(table_output, "content") else str(table_output)
        if output_file:
            log_to_file(output_file, {"type": "Table", "query": query, "headers": headers_list, "table_output": text})

        return text

    def export_to_csv(markdown_text):
        lines = markdown_text.strip().split("\n")
        rows = []
        for line in lines:
            if re.match(r"^\s*\|?[\s:-]+\|[\s:-]+", line):
                continue
            cells = [c.strip(" |") for c in line.split("|") if c.strip()]
            if cells:
                rows.append(cells)

        if len(rows) < 2:
            return None  
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="", encoding="utf-8-sig")
        writer = csv.writer(temp)
        for row in rows:
            writer.writerow(row)
        temp.close()
        return temp.name
    
    def download_log(output_file):
        return output_file if os.path.exists(output_file) else None



    # --- GRADIO UI ---
    with gr.Blocks(theme="soft") as demo:
        gr.Markdown("# 🧠 RAG Configuration and Interface")

        with gr.Accordion("System Configuration", open=True):
            llm_provider = gr.Dropdown(["gemini", "openai", "ollama"], label="LLM Provider", value="gemini")
            llm_model = gr.Textbox(label="LLM Model", value="gemini-2.5-flash-lite")

            emb_provider = gr.Dropdown(["gemini", "openai", "ollama"], label="Embedding Provider", value="ollama")
            emb_model = gr.Textbox(label="Embedding Model", value="nomic-embed-text")

            api_key = gr.Textbox(label="API Key", placeholder="Enter your API Key if needed", type="password")

            persist_dir = gr.Textbox(label="Persist Directory", value="./chroma_db")
            output_file = gr.Textbox(label="Output File", value="output.json")

        with gr.Tabs():
            with gr.TabItem("Simple Q&A"):
                query = gr.Textbox(label="Your Query")
                output = gr.Markdown(label="Response")
                run_btn = gr.Button("🔍 Run Query", variant="primary")

                run_btn.click(
                    fn=simple_qa_with_chain,
                    inputs=[query, llm_provider, llm_model, emb_provider, emb_model, api_key, persist_dir, output_file],
                    outputs=output
                )


            with gr.TabItem("Table Generator"):
                query_t = gr.Textbox(label="Your Query")
                headers_t = gr.Textbox(label="Headers (comma-separated)")
                output_t = gr.Markdown(label="Generated Table")
                export_btn = gr.Button("⬇️ Export as CSV", variant="secondary")
                run_table_btn = gr.Button("📊 Generate Table", variant="primary")

                run_table_btn.click(
                    fn=generate_table_with_chain,
                    inputs=[query_t, headers_t, llm_provider, llm_model, emb_provider, emb_model, api_key, persist_dir, output_file],
                    outputs=output_t
                )

                export_btn.click(
                    fn=export_to_csv,
                    inputs=output_t,
                    outputs=gr.File(label="Download CSV")
                )
            with gr.TabItem("Download Log"):
                log_output = gr.File(label="Download Interaction Log")
                download_btn = gr.Button("⬇️ Download Log", variant="primary")

                download_btn.click(
                    fn=download_log,
                    inputs=output_file,
                    outputs=log_output
                )

    demo.launch(inbrowser=True)
