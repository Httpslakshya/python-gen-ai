from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import requests
load_dotenv()

def weather(city:str):
    url=f"http://wttr.in/{city.lower}?format=%C+%t"
    respones=requests.get(url)
    if respones.status_code==200:
        return f"current weather in indore is : {respones.text}"
    else:
        return "unable to get data"

available_tools = {
     "weather":weather
}

SYSTEM_PROMPT= """
you are an expert ai assitant is resolving user queries using chain of throught method
you work on START, PLAN .and OUTPUT steps.
you need to first PLAN what needs to be done ,the PLAN can be multiple steps.
once you think enough PLAN has been done ,finally you can give OUTPUT.
You can also call a tools if required from the list of available tools.
for every tool call wait for the observe step which is the output from the called tool.

Rules:
- Strictly follow the given JSON output format.
- Only one step at a time
- the sequence of step is START (where user gives an input),PLAN (that can be multiple times ) and finally OUTPUT (whic is going to the displayed to the user).

Output JSON Format:
{"step" : "START" | "PLAN"  | "OUTPUT" | "TOOL" , "content":"string","tool":"string","input":"string"}

Available tools:
-weather(city): take city name as an input string and returns the weather info about the city

Example 1:
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

Example 2:
START: what is the current weather of delhi
PLAN:{"step":"PLAN":"content":"seems like user is intrested in getting weather info of delhi in india"}
PLAN:{"step":"PLAN":"content":"lets see if we have any tool for this from list of available tool"}
PLAN:{"step":"PLAN":"content":"Great, we have weather tool from the available tool for this query"}
PLAN:{"step":"PLAN":"content":"I need to call weather tool for delhi as input for city"}
PLAN:{"step":"TOOL": "tool":"weather","input":"delhi"}
PLAN:{"step":"OBSERVE":"tool":"weather","output":"haze with 20 C"}
PLAN:{"step":"PLAN":"content":"Great i got the weather info about delhi"}
OUTPUT:{"step":"OUTPUT":"content":"the current weather in delhi is haze with some mist and the temp is 20C"}

"""

client = OpenAI(
    #api_key=api_key, these is okay too
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

user_query = input("👉🏻 ")
message_history.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model="gemini-2.0-flash",   # 🔥 use gemini model
        response_format={"type": "json_object"},
        messages=message_history
    )

    raw_result = response.choices[0].message.content

    # 🔥 safety (Gemini kabhi kabhi JSON break karta hai)
    try:
        parsed_result = json.loads(raw_result)
    except:
        print("⚠️ JSON Error, raw output:", raw_result)
        break

    # append AFTER parsing (safe)
    message_history.append({
        "role": "assistant",
        "content": raw_result
    })

    step = parsed_result.get("step")
    content = parsed_result.get("content")

    if step == "START":
        print("🔥", content)
        continue

    elif step == "PLAN":
        print("🧠", content)
        continue

    elif step == "TOOL":
        tool_to_call = parsed_result.get("tool")
        tool_input = parsed_result.get("input")
        print(f"💀 : {tool_to_call} ({tool_input}) = {tool_response}")

        tool_response = available_tools[tool_to_call](tool_input)
        message_history.append({"role":"developer" , "content": json.dumps(
            { "step":"OBSERVE","tool":"tool_to_call", "input": tool_input , "output":tool_response}
        )})

        continue

    elif step == "OUTPUT":
        print("🤖", content)
        break

print("\n\n\n")
