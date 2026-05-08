from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
import os
from openai import OpenAI

load_dotenv() 

QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
QDRANT_URL=os.getenv("QDRANT_URL")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
#vector embedding
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db=QdrantVectorStore.from_existing_collection( 

    embedding=embedding_model,
    url=QDRANT_URL,
    collection_name="agentic_ai_ud",
    #prefer_grpc=True,
    #api_key=QDRANT_API_KEY,
 )

#Take the user input
user_query= input("ask something=>")
#return relevant chunks from vector db
search_results = vector_db.similarity_search(query=user_query)

context = "\n\n\n".join([
    f"Page Content: {result.page_content}\n"
    f"Page Number: {result.metadata['page_label']}\n"
    f"File Location: {result.metadata['source']}"
    for result in search_results
])

SYSTEM_PROMPT= f"""
You are a helpfull AI Assistant who answers user query based on the available 
context retrieved from a PDF file along with the page_contents and page number.

You should only ans the user based on the following context and navigate the user to open the right page number to know more.

Context:
{context}
"""


client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"        
)

response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",             
                
                temperature=0.2,            # lower = more reliable JSON
                messages=[
                    {"role":"system", "content":SYSTEM_PROMPT },
                    {"role":"user", "content":user_query },
                ]
            )

print(f"🤖: {response.choices[0].message.content}")