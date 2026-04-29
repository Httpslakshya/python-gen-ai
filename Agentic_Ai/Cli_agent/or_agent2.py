from dotenv import load_dotenv
import os
import json
import requests
import subprocess

load_dotenv()

# 🔥 OpenRouter Config
API_KEY = os.getenv("OPEN_ROUTER_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 🔧 TOOL
def run_command(cmd: str):

    # ⚠️ Basic safety
    blocked = ["rm", "shutdown", "reboot", "del", "format"]

    for word in blocked:
        if word in cmd.lower():
            return "Blocked dangerous command"

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    return result.stdout if result.stdout else result.stderr


available_tools = {
    "run_command": run_command
}

# 🧠 SYSTEM PROMPT
SYSTEM_PROMPT = """
You are an AI agent.

Flow:
START → PLAN → TOOL → OUTPUT

Rules:
- Return ONLY valid JSON.
- One step at a time.
- Wait for tool output after TOOL.

Format:
{
 "step":"START|PLAN|TOOL|OUTPUT",
 "content":"string",
 "tool":"string",
 "input":"string"
}

Tools:
- run_command(cmd:str): runs terminal commands.
"""

# 💬 CHAT HISTORY
message_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# 👤 USER INPUT
user_query = input("👉🏻 ")
message_history.append({
    "role": "user",
    "content": user_query
})

while True:

    data = {
        # ✅ FREE working model
        "model": "meta-llama/llama-3-8b-instruct",

        "messages": message_history
    }

    response = requests.post(
        URL,
        headers=HEADERS,
        json=data
    )

    result = response.json()

    try:
        raw_result = result["choices"][0]["message"]["content"]
    except:
        print("⚠️ API Error:", result)
        break

    # 🔥 extract json safely
    try:
        start = raw_result.find("{")
        end = raw_result.rfind("}") + 1

        raw_result = raw_result[start:end]

        parsed_result = json.loads(raw_result)

    except Exception as e:
        print("⚠️ JSON Error:", raw_result)
        break

    # save assistant response
    message_history.append({
        "role": "assistant",
        "content": raw_result
    })

    step = parsed_result.get("step")
    content = parsed_result.get("content")

    # 🚀 START
    if step == "START":
        print("🔥", content)

    # 🧠 PLAN
    elif step == "PLAN":
        print("🧠", content)

    # 🛠 TOOL
    elif step == "TOOL":

        tool_to_call = parsed_result.get("tool")
        tool_input = parsed_result.get("input")

        tool_response = available_tools[tool_to_call](tool_input)

        print(f"💀 {tool_to_call}({tool_input})")
        print("📦", tool_response)

        # send observation back
        message_history.append({
            "role": "user",
            "content": json.dumps({
                "step": "OBSERVE",
                "tool": tool_to_call,
                "output": tool_response
            })
        })

    # ✅ OUTPUT
    elif step == "OUTPUT":
        print("🤖", content)
        break