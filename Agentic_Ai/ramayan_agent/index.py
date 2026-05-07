from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from dotenv import load_dotenv
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore


load_dotenv()
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
QDRANT_URL=os.getenv("QDRANT_URL")
pdf_path = Path(__file__).parent / "ramayan-eng.pdf"

#load the file in python program
loader = PyPDFLoader(pdf_path)
docs = loader.load()
#spilt the docs into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size =1000,
    chunk_overlap=400
)

chunks=text_splitter.split_documents(documents=docs)
for chunk in chunks:
    chunk.metadata["filename"] = pdf_path.name

#vector embedding
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = QdrantVectorStore.from_documents(
    #force_recreate=True,
    documents=chunks,
    embedding=embedding_model,
    url=QDRANT_URL,
    collection_name="agentic_ai_ud",
    prefer_grpc=True,
    api_key=QDRANT_API_KEY,
)

print("indexing of document done")

