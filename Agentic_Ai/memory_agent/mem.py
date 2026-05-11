from mem0 import Memory
import os
from dotenv import load_dotenv
from openai import OpenAI
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

user_query = input("👱 : ")
response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",             
                
                temperature=0.2,            # lower = more reliable JSON
                messages=[
                  
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