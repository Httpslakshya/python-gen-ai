from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

# 🔥 OpenRouter setup
URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPEN_ROUTER_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 🔧 TOOL
def weather(city: str):
    url = f"http://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"current weather in {city} is : {response.text}"
    else:
        return "unable to get data"

available_tools = {
    "weather": weather
}

# 🧠 SYSTEM PROMPT
SYSTEM_PROMPT = """(same as yours, no change needed)"""

# 💬 MESSAGE HISTORY
message_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

user_query = input("👉🏻 ")
message_history.append({"role": "user", "content": user_query})


while True:

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": message_history,
        "response_format": {"type": "json_object"}  # ⚠️ not always respected
    }

    response = requests.post(URL, headers=headers, json=data)
    result = response.json()

    try:
        raw_result = result["choices"][0]["message"]["content"]
    except:
        print("⚠️ API Error:", result)
        break

    # 🔥 JSON parse
    try:
        parsed_result = json.loads(raw_result)
    except:
        print("⚠️ JSON Error:", raw_result)
        break

    message_history.append({
        "role": "assistant",
        "content": raw_result
    })

    step = parsed_result.get("step")
    content = parsed_result.get("content")

    if step == "START":
        print("🔥", content)

    elif step == "PLAN":
        print("🧠", content)

    elif step == "TOOL":
        tool_to_call = parsed_result.get("tool")
        tool_input = parsed_result.get("input")

        tool_response = available_tools[tool_to_call](tool_input)

        print(f"💀 : {tool_to_call} ({tool_input}) = {tool_response}")

        message_history.append({
            "role": "user",   # ⚠️ important change
            "content": json.dumps({
                "step": "OBSERVE",
                "tool": tool_to_call,
                "output": tool_response
            })
        })

    elif step == "OUTPUT":
        print("🤖", content)
        break