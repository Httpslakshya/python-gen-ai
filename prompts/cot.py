from dotenv import load_dotenv
from openai import OpenAI
import os
import json

load_dotenv()

SYSTEM_PROMPT= """
you are an expert ai assitant is resolving user queries using chain of throught method
you work on START, PLAN .and OUTPUT steps.
you need to first PLAN what needs to be done ,the PLAN can be multiple steps.
once you think enough PLAN has been done ,finally you can give OUTPUT.
Rules:
- Strictly follow the given JSON output format.
-only run one step at a time
- the sequence of step is START (where user gives an input),PLAN (that can be multiple times ) and finally OUTPUT (whic is going to the displayed to the user).

Output JSON Format:
{"step" : "START" | "PLAN"  | "OUTPUT" , "content":"string"}
Example:
START: hey can you solve 2+3 * 5 / 10
PLAN:{"step":"PLAN":"content":"looking at the problem we should solve this using BODMAS method"}
PLAN:{"step":"PLAN":"content":"Yes, The BODMAS is correct thing to be done here"}
PLAN:{"step":"PLAN":"content":"first we must multiply 3* 5 which is 15"}
PLAN:{"step":"PLAN":"content":"Now the new Eqution is 2 + 15/10"}
PLAN:{"step":"PLAN":"content":"We must perform divide thats 15 / 10 =1.5"}
PLAN:{"step":"PLAN":"content":"Now the new equation is 2 + 1.5"}
PLAN:{"step":"PLAN":"content":"now finally perform the add "}
PLAN:{"step":"PLAN":"content":"Great, we have solve and finally left with 3.5 as ans"}
OUTPUT:{"step":"OUTPUT":"content":"3.5"}
"""

client = OpenAI(
    #api_key=api_key, these is okay too
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response=client.chat.completions.create(
    model="gemini-3-flash-preview",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "hey write a code to add n numbers in js"},
        {"role": "assistant", "content": json.dumps() }

    ]
)

print(response.choices[0].message.content)
