from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import requests
load_dotenv()

def run_command(cmd:str):
    result =os.system(cmd)
    return result



available_tools = {
     "run_command": run_command
}

SYSTEM_PROMPT = """
You are an AI assistant that solves user queries using step-by-step reasoning.

Workflow:
1. START → Understand the user's request.
2. PLAN → Think and break the task into smaller steps (can appear multiple times).
3. TOOL → Use a tool if needed.
4. OUTPUT → Final response for the user.

Rules:
- Return ONLY valid JSON.
- Only one step at a time.
- Wait for tool output after every TOOL step.
- Keep responses concise.

JSON Format:
{
  "step": "START" | "PLAN" | "TOOL" | "OUTPUT",
  "content": "string",
  "tool": "string",
  "input": "string"
}

Available Tools:
- run_command(cmd:str)
  Executes a Linux command on the user's system.

Example:

User: "Show current directory"

Assistant:
{"step":"START","content":"User wants to know the current directory.","tool":"","input":""}

Assistant:
{"step":"PLAN","content":"Use pwd command to get current directory.","tool":"","input":""}

Assistant:
{"step":"TOOL","content":"Running pwd command.","tool":"run_command","input":"pwd"}

Tool Output:
/home/lakshya

Assistant:
{"step":"OUTPUT","content":"Current directory is /home/lakshya","tool":"","input":""}
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
        model="gemini-2.0-flash-lite",   # 🔥 use gemini model
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
