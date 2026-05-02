from dotenv import load_dotenv
import os
import json
import requests
import subprocess
import re

load_dotenv()

API_KEY = os.getenv("OPEN_ROUTER_KEY")
URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ── Tools ──────────────────────────────────────────────────────────────────────

def run_command(cmd: str) -> str:
    blocked = ["rm -rf", "shutdown", "reboot", "format"]
    for word in blocked:
        if word in cmd.lower():
            return f"Blocked dangerous command: '{word}' detected."
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout.strip() or result.stderr.strip()
    return output or "(no output)"

AVAILABLE_TOOLS = {
    "run_command": run_command
}

# ── System Prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a terminal automation agent. You MUST respond with ONLY a single valid JSON object — no markdown, no extra text, no explanation outside the JSON.

Workflow: START → PLAN → TOOL (repeat if needed) → OUTPUT

JSON Schema (always use ALL four keys):
{
  "step": "START" | "PLAN" | "TOOL" | "OUTPUT",
  "content": "<description of what you are doing>",
  "tool": "<tool name or null>",
  "input": "<tool input string or null>"
}

Available tools:
- run_command: runs a shell command and returns stdout/stderr.

Rules:
- ONE JSON object per response, nothing else.
- Use null (not "None") for unused fields.
- After a TOOL step, wait for the OBSERVE message before continuing.
- Windows shell is used — use Windows-compatible commands (mkdir, echo, type, etc.).
- Only emit OUTPUT when the task is fully complete.
"""

# ── JSON Extractor (robust) ────────────────────────────────────────────────────

def extract_json(text: str) -> dict:
    """
    Tries multiple strategies to extract a JSON object from model output.
    Raises ValueError if nothing works.
    """
    if not text or text.strip().lower() in ("none", "null", ""):
        raise ValueError(f"Model returned empty/null: {text!r}")

    # Strategy 1: strip markdown code fences then parse
    cleaned = re.sub(r"```(?:json)?|```", "", text).strip()

    # Strategy 2: find the outermost { ... } block
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in: {cleaned!r}")

    json_str = cleaned[start:end]
    return json.loads(json_str)  # raises json.JSONDecodeError on bad JSON

# ── Main Agent Loop ────────────────────────────────────────────────────────────

message_history = [{"role": "system", "content": SYSTEM_PROMPT}]

user_query = input("👉  ")
message_history.append({"role": "user", "content": user_query})

MAX_STEPS = 15

for step_num in range(MAX_STEPS):

    payload = {
        # Switch to a stronger instruction-following model
        "model": "meta-llama/llama-3.1-8b-instruct",
        # Alternatively try: "mistralai/mistral-7b-instruct"
        # Or (paid but very reliable): "openai/gpt-4o-mini"
        "messages": message_history,
        "temperature": 0.2,         # lower = more deterministic / JSON-safe
        "response_format": {"type": "json_object"},  # forces JSON on supported models
    }

    response = requests.post(URL, headers=HEADERS, json=payload)
    result = response.json()

    # ── API-level error ────────────────────────────────────────────────────────
    if "choices" not in result:
        print("⚠️  API Error:", json.dumps(result, indent=2))
        break

    raw = result["choices"][0]["message"]["content"]

    # ── Parse JSON ────────────────────────────────────────────────────────────
    try:
        parsed = extract_json(raw)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"⚠️  JSON parse error (step {step_num}): {e}")
        print(f"   Raw output was: {raw!r}")
        # Give the model a chance to self-correct
        message_history.append({
            "role": "user",
            "content": (
                '{"step":"OBSERVE","output":"ERROR: Your last response was not valid JSON. '
                'Return ONLY a single JSON object matching the schema, with no extra text."}'
            )
        })
        continue

    # Save valid assistant turn
    clean_json_str = json.dumps(parsed)
    message_history.append({"role": "assistant", "content": clean_json_str})

    step    = parsed.get("step", "").upper()
    content = parsed.get("content", "")

    # ── Dispatch ──────────────────────────────────────────────────────────────
    if step == "START":
        print(f"🔥  {content}")

    elif step == "PLAN":
        print(f"🧠  {content}")

    elif step == "TOOL":
        tool_name  = parsed.get("tool")
        tool_input = parsed.get("input")

        if tool_name not in AVAILABLE_TOOLS:
            obs_output = f"Error: unknown tool '{tool_name}'."
        else:
            print(f"🛠️   {tool_name}({tool_input!r})")
            obs_output = AVAILABLE_TOOLS[tool_name](tool_input)
            print(f"📦  {obs_output}")

        message_history.append({
            "role": "user",
            "content": json.dumps({
                "step": "OBSERVE",
                "tool": tool_name,
                "output": obs_output
            })
        })

    elif step == "OUTPUT":
        print(f"🤖  {content}")
        break

    else:
        print(f"⚠️  Unknown step '{step}' — raw: {raw!r}")
        break

else:
    print("⚠️  Reached max steps without OUTPUT.")


