from dotenv import load_dotenv
import os
import requests
load_dotenv()
url="https://openrouter.ai/api/v1/chat/completions"
API_KEY= os.getenv("OPEN_ROUTER_KEY")
headers ={
    "Authorization": f"Bearer {API_KEY}",
    "Content-type" : "application/json"
}
data ={
    "model": "meta-llama/llama-3-8b-instruct",
    "messages": [
        {"role":"user" ,"content":"hello there"}
    ]
}

response = requests.post(url,headers=headers,json=data)

result =response.json()
print(result["choices"][0]["message"]["content"])