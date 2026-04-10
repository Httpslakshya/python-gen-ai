import requests
import os
from dotenv import load_dotenv
url = "https://openrouter.ai/api/v1/chat/completions"
load_dotenv()
OPEN_ROUTER_KEY=os.getenv("OPEN_ROUTER_KEY")
headers = {
    "Authorization": f"Bearer {OPEN_ROUTER_KEY}",
    "Content-Type": "application/json"
}

def send_request(url, headers, data):
    try:
        response = requests.post(url, headers=headers, json=data) # Check if the request was successful
        return response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def chat():
        while True:
            input_data = input("Enter your message: ")
            data = {
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {"role": "user", "content": "give me reply for this in short: " + input_data}
                ]
            }
            
            if input_data != "none":
                response = send_request(url, headers, data)    
                result = response.json()
                print(result["choices"][0]["message"]["content"])
            else:
                return
chat()


