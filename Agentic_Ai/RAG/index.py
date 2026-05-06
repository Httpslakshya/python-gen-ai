from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

pdf_path = Path(__file__).parent / "ramayan-eng.pdf"


loader = PyPDFLoader(pdf_path)
docs = loader.load()
print(docs[25])