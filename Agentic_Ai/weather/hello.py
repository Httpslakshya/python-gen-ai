from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
#api_key=os.getenv("GEMINI_API_KEY")
client = OpenAI(
    #api_key=api_key, these is okay too
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response=client.chat.completions.create(
    model="gemini-3-flash-preview",
    messages=[
        {"role": "user", "content": "hello"} 
    ]
)

print(response.choices[0].message.content)





