from dotenv import load_dotenv
import os
from .server import app
import uvicorn

load_dotenv()
GROQ_API_KEY=os.getenv("GROQ_API_KEY")

def main():
    uvicorn.run(app, port=8000,host="0.0.0.0")

main()