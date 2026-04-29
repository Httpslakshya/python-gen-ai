from dotenv import load_dotenv
from openai import OpenAI
import os
import requests
load_dotenv()
#api_key=os.getenv("GEMINI_API_KEY")
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def weather(city:str):
    url=f"http://wttr.in/{city.lower}?format=%C+%t"
    respones=requests.get(url)
    if respones.status_code==200:
        print(f"current weather in indore is : {respones.text}")

def main():
    user_query = input(">")
    response = client.chat.completions.create(
        model="gemini-3-flash-preview",
        messages=[
            {"role":"system","content":"you are an expert ai assistant,that can tell current weather too by calling inbuild function or calling the function weather(city)"},
            {"role": "user", "content": user_query} 
        ]
    )
    print("💀: ",response.choices[0].message.content)

#main()
city=input(">")
weather(city=city) 