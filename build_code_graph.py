import os
import pickle
import time
from dotenv import load_dotenv
from tqdm import tqdm

from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import PythonCodeTextSplitter
from langchain.docstore.document import Document

# --- 1. SET UP THE ENVIRONMENT ---
load_dotenv()
print("✅ Environment variables loaded.")

# --- CONFIGURATION ---
SOURCE_CODE_ROOT = "source_code/requests"
DATA_OUTPUT_DIR = "data"
FORCE_REGENERATE_SUMMARIES = False

# --- Helper Function: Retry with backoff ---
def retry_with_backoff(func, max_retries=5, initial_delay=5):
    retries = 0
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            wait_time = initial_delay * (2 ** retries)
            print(f"⚠️ Retry {retries+1}/{max_retries} after {wait_time}s due to: {e}")
            time.sleep(wait_time)
            retries += 1
    raise RuntimeError("❌ Max retries exceeded.")

# --- 2. AST PARSER ---
def extract_code_elements(root_dir):
    all_elements = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                splitter = PythonCodeTextSplitter(chunk_size=1500, chunk_overlap=200)
                elements = splitter.create_documents([content])
                for i, element in enumerate(elements):
                    element.metadata["file_path"] = file_path
                    element.metadata["start_index"] = i
                all_elements.extend(elements)
    return all_elements

# --- 3. SMART SUMMARIZER ---
def generate_summaries(code_elements, force_regenerate=False):
    summaries_path = os.path.join(DATA_OUTPUT_DIR, "summaries.pkl")
    existing_summaries = []
    summarized_keys = set()

    if os.path.exists(summaries_path):
        print("📦 Loading existing summaries from disk...")
        with open(summaries_path, "rb") as f:
            existing_summaries = pickle.load(f)
            summarized_keys = {
                (doc.metadata["file_path"], doc.metadata.get("start_index", i))
                for i, doc in enumerate(existing_summaries)
            }

    if not force_regenerate:
        code_elements = [
            el for i, el in enumerate(code_elements)
            if (el.metadata["file_path"], el.metadata.get("start_index", i)) not in summarized_keys
        ]

    print(f"🧠 Summarizing {len(code_elements)} new code elements...")
    summarization_llm = GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
    new_summaries = []

    for idx, element in enumerate(tqdm(code_elements, desc="Generating Summaries")):
        prompt = f"""
        Please provide a concise, one-sentence summary of the following Python code.
        Focus on its primary purpose and functionality.

        Code:
        ```python
        {element.page_content}
        ```

        One-sentence summary:
        """
        try:
            summary_text = retry_with_backoff(lambda: summarization_llm.invoke(prompt))
            doc = Document(page_content=summary_text, metadata=element.metadata.copy())
            new_summaries.append(doc)
        except Exception as e:
            print(f"❌ Error summarizing {element.metadata['file_path']}: {e}")
            continue

    all_summaries = existing_summaries + new_summaries
    with open(summaries_path, "wb") as f:
        pickle.dump(all_summaries, f)

    print(f"✅ Saved total {len(all_summaries)} summaries.")
    return all_summaries

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("--- Phase 3: Building the Code Graph ---")
    os.makedirs(DATA_OUTPUT_DIR, exist_ok=True)

    print("1. Parsing the codebase to extract functions and classes...")
    code_elements = extract_code_elements(SOURCE_CODE_ROOT)
    print(f"✅ Found {len(code_elements)} code elements.")

    with open(os.path.join(DATA_OUTPUT_DIR, "code_elements.pkl"), "wb") as f:
        pickle.dump(code_elements, f)
    print(f"✅ Raw code elements saved to {DATA_OUTPUT_DIR}/code_elements.pkl")

    print("\n2. Generating LLM-based summaries (resume supported)...")
    summaries = generate_summaries(code_elements, force_regenerate=FORCE_REGENERATE_SUMMARIES)
    print(f"✅ Total summaries stored: {len(summaries)}")

    print("\n--- Preprocessing Complete ---")
    print("You can now run the query script: `python phase3_query_assistant.py`")