from pathlib import Path
from typing import List, Union,Any,Tuple
from langchain_community.document_loaders import PyMuPDFLoader


def load_all_documents(data_dir: str) -> List[Any]:
    """Load all documents from the specified directory.

    Args:
        data_dir (str): The directory containing the documents.
    """
    data_path = Path(data_dir).resolve()
    print(f"[DEBUG] Loading documents from: {data_path}")
    documents = []

    pdf_files = list(data_path.glob("**/*.pdf"))
    print(f"[DEBUG] Found {len(pdf_files)} PDF files: {[str(f) for f in pdf_files]}")
    for pdf_file in pdf_files:
        print(f"[DEBUG] Loading PDF file: {pdf_file}")
        try:
            loader = PyMuPDFLoader(str(pdf_file))
            loader = loader.load()
            print(f"[DEBUG] Loaded {len(loader)} pages from {pdf_file}")
            documents.extend(loader)
        except Exception as e:
            print(f"[ERROR] Failed to load {pdf_file}: {e}")  
 
    # #JSON files
    # text_files = list(data_path.glob("**/*.json"))
    # print(f"[DEBUG] Found {len(text_files)} JSON files: {[str(f) for f in text_files]}")
    # for text_file in text_files:
    #     print(f"[DEBUG] Loading JSON file: {text_file}")
    #     try:
    #         loader = JSONLoader(str(text_file))
    #         loader = loader.load()
    #         print(f"[DEBUG] Loaded {len(loader)} records from {text_file}")
    #         documents.extend(loader)
    #     except Exception as e:
    #         print(f"[ERROR] Failed to load {text_file}: {e}")   
    # # txt files
    # text_files = list(data_path.glob("**/*.txt"))
    # print(f"[DEBUG] Found {len(text_files)} text files: {[str(f) for f in text_files]}")
    # for text_file in text_files:
    #     print(f"[DEBUG] Loading text file: {text_file}")
    #     try:
    #         with open(text_file, 'r', encoding='utf-8') as f:
    #             content = f.read()
    #             documents.append({"text": content, "metadata": {"source": str(text_file)}})
    #         print(f"[DEBUG] Loaded text from {text_file}")
    #     except Exception as e:
    #         print(f"[ERROR] Failed to load {text_file}: {e}")
    return documents








