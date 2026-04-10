from google import genai 
import os
from dotenv import load_dotenv

load_dotenv()
api_key =os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key)
response= client.models.generate_content(
    model="gemini-2.5-flash",contents="Explain how ai work in summary"

)
print(response.text)