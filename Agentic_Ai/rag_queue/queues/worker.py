from langchain_huggingface import HuggingFaceEmbeddings
from openai import OpenAI
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
import os

load_dotenv()

# Groq Client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Embedding Model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Qdrant Vector DB
vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="agentic_ai_ud",
)

def process_query(query: str):

    print("Searching Chunks...", query)

    # Retrieve relevant chunks
    search_results = vector_db.similarity_search(
        query=query,
        k=3
    )

    # Build Context
    context = "\n\n".join([
        f"""
        Page Content: {result.page_content}

        Page Number: {result.metadata.get('page', 'Unknown')}

        File Location: {result.metadata.get('source', 'Unknown')}
        """
        for result in search_results
    ])

    # System Prompt
    SYSTEM_PROMPT = f"""
    You are a helpful AI assistant.

    Answer the user's question ONLY from the provided context.

    Explain clearly and concisely.

    If the answer is not found in the context, say:
    "I could not find this information in the document."

    Context:
    {context}
    """

    # Generate Response
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )

    return response.choices[0].message.content


# Chat Loop
# while True:

#     user_query = input("\nAsk something => ")

#     if user_query.lower() == "exit":
#         break

#     answer = process_query(user_query)

#     print("\n🤖:", answer)

