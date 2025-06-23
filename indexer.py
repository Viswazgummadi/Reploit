# File: indexer.py
import os
import shutil
import time
import tempfile # <--- IMPORT THE CORRECT LIBRARY
from git import Repo
from tqdm import tqdm
# No need to import pinecone here, as it's handled by langchain_pinecone

from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import PythonCodeTextSplitter
from langchain.docstore.document import Document
from langchain_pinecone import PineconeVectorStore
from config import GOOGLE_API_KEY, PINECONE_INDEX_NAME

# Initialize the single embedding model needed for upserting
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

def _extract_code_elements(repo_path):
    """Walks through the directory, finds .py files, and extracts functions/classes."""
    all_elements = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    splitter = PythonCodeTextSplitter(chunk_size=1000, chunk_overlap=100)
                    elements = splitter.create_documents([content])
                    for element in elements:
                        element.metadata["file_path"] = os.path.normpath(file_path)
                    all_elements.extend(elements)
                except Exception as e:
                    print(f"Could not process file {file_path}: {e}")
    return all_elements

def _generate_summaries(code_elements, llm: GoogleGenerativeAI):
    """Generates a one-sentence summary for each code element, respecting rate limits."""
    print("ℹ️ Generating new summaries. This will be slow to respect API rate limits.")
    summaries = []
    
    for element in tqdm(code_elements, desc="Generating Summaries"):
        prompt = f"Please provide a concise, one-sentence summary of the following Python code:\n\n```python\n{element.page_content}\n```\n\nOne-sentence summary:"
        
        try:
            summary_text = llm.invoke(prompt)
            summary_doc = Document(page_content=summary_text, metadata=element.metadata.copy())
            summaries.append(summary_doc)
        except Exception as e:
            print(f"Error generating summary for element in {element.metadata['file_path']}: {e}")
            continue
        finally:
            time.sleep(4.1) # Rate limit to stay under 15 requests/minute

    return summaries

def process_and_index_repo(repo_url: str, llm: GoogleGenerativeAI):
    """Clones, processes, and indexes a repo into Pinecone."""
    # --- THIS IS THE CORRECTED LOGIC ---
    # Use a secure, temporary directory outside of the project folder.
    # The 'with' statement ensures it's automatically cleaned up.
    with tempfile.TemporaryDirectory() as repo_path:
        try:
            print(f"Cloning repository into temporary directory: {repo_path}")
            Repo.clone_from(repo_url, repo_path, depth=1)

            print("1. Parsing codebase...")
            code_elements = _extract_code_elements(repo_path)
            print(f"✅ Found {len(code_elements)} code elements.")

            print("\n2. Generating summaries...")
            summaries = _generate_summaries(code_elements, llm)
            print(f"✅ Generated {len(summaries)} summaries.")
            
            print("\n3. Upserting to Pinecone...")
            PineconeVectorStore.from_documents(
                documents=code_elements, embedding=embeddings, 
                index_name=PINECONE_INDEX_NAME, namespace="code-chunks"
            )
            print("✅ Upserted code chunks.")
            PineconeVectorStore.from_documents(
                documents=summaries, embedding=embeddings, 
                index_name=PINECONE_INDEX_NAME, namespace="summaries"
            )
            print("✅ Successfully upserted all data to Pinecone.")
            return "Indexing complete."
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            return f"Error: {e}"
        # No 'finally' block needed for cleanup, 'with' handles it!