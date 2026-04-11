#few shot prompting 

#In few shot prompting we Ask a model to do something directly without showing it how, relying on its pretrained data. and also give ai some examples 


from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
SYSTEM_PROMPT = "you are an mathematical expert and your name is deepak , act as a teacher and answer only mathematics related question , " \
"if not related to maths say something like sorry ask only maths related questions . for example " \
"Q: hey explain me coding" \
"A: i can only answer maths related question"

client = OpenAI(

    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response=client.chat.completions.create(
    model="gemini-3-flash-preview",
    
    
    messages=[
        {"role": "system" ,"content": SYSTEM_PROMPT},
        {"role": "user", "content": "write a hello world code in cpp"} 
    ]
)

print(response.choices[0].message.content)





