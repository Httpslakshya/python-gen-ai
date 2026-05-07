from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from dotenv import load_dotenv
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore


load_dotenv()
GOOGLE_API_KEY=os.getenv("GEMINI_API_KEY")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")

pdf_path = Path(__file__).parent / "pythonguide.pdf"

#load the file in python program
loader = PyPDFLoader(pdf_path)
docs = loader.load()
#spilt the docs into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size =1000,
    chunk_overlap=400,
)

chunks=text_splitter.split_documents(documents=docs)

#vector embedding
embedding_model =GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
    )

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="https://49d86bb4-d70c-49ca-9ed7-a99bcb59508a.us-east-2-0.aws.cloud.qdrant.io:6333",
    collection_name="agentic_ai_ud",
    prefer_grpc=True,
    api_key=QDRANT_API_KEY,
)

print("indexing of document done")

