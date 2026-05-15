import requests
from dotenv import load_dotenv
import os
load_dotenv()

BASE_URL = "https://api.freemodel.dev"
API_KEY=os.getenv("OPENAI_API_KEY")
response = requests.post(
    f"{BASE_URL}/v1/responses",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    },
    json={
        "model": "gpt-5.5",
        "instructions": "You are a helpful assistant.",  # system prompt
        "input": "you are an senior full stack developer agent , you have to create a folder in current dir and name it weather, in that folder create a weather app with good styling and working, use the weather logic from line 28-34 in the file agent.py in current dir",
        "temperature": 1.0,
        "reasoning": {"effort": "medium"}               # low / medium / high / xhigh
    }
)

data = response.json()

if response.status_code == 200:
    print(data["output"][0]["content"][0]["text"])
else:
    print(f"Error {response.status_code}: {data}")