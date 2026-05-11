from mem0 import Memory
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
#from langchain_huggingface import HuggingFaceEmbeddings
load_dotenv()

api_key=os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"        
)
config = {
    "version":"v1.1",
     "embedder": {
         "provider":"huggingface",
         "config":{
             "model":"sentence-transformers/all-MiniLM-L6-v2",
              "embedding_dims": 384
              } # "api_key":OPENAI_API_KEY," openai model use karw toh
     },
     "llm":{
         "provider":"groq",
         "config":{"api_key":api_key ,"model":"llama-3.3-70b-versatile"}
     },
     "vector_store":{
         "provider":"qdrant",
         "config":{
             "host":"localhost",
             "port":6333,
             "collection_name": "lakshya_memory",
              "embedding_model_dims": 384
         }
     }
}

mem_client =Memory.from_config(config)

while True:

    user_query = input("👱 : ")

    search_memory = mem_client.search(
        query=user_query,
        filters={"user_id": "lakshyadharkar"}
    )

    

    memories = [
        f"ID: {mem.get("id")}\nMemory: {mem.get("memory")}"
          for mem in search_memory.get("results") 
    ]
 
    SYSTEM_PROMPT = f"""
    here is the context about the user:
    {json.dumps(memories)}
    """

    response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",             
                
                temperature=0.2,            # lower = more reliable JSON
                messages=[
                    {"role":"system", "content":SYSTEM_PROMPT },
                    {"role":"user", "content":user_query },
                ]
            )
    ai_response = response.choices[0].message.content
    print(f"🤖: ",ai_response)

    mem_client.add(
    user_id="lakshyadharkar",
    messages=[
        {"role": "user","content":user_query},
        {"role": "assistant", "content": ai_response}
        ]
    )

    print("✅memory saved")