from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import time
import subprocess

load_dotenv()


# ─────────────────────────────────────────────
# Tool Functions
# ─────────────────────────────────────────────

def run_command(cmd: str) -> str:
    """Runs a shell command safely and returns its output."""
    blocked = ["rm -rf", "shutdown", "reboot", "format"]
    for word in blocked:
        if word in cmd.lower():
            return f"Blocked dangerous command: '{word}' detected."
 
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout.strip() or result.stderr.strip()
    return output or "(no output)"
 
 
def write_file(input_str: str) -> str:
    """
    Writes content to a file.
    Expects input as JSON string: {"path": "folder/file.txt", "content": "..."}
    Creates parent folders automatically.
    """
    try:
        data = json.loads(input_str)
        path    = data.get("path", "").strip()
        content = data.get("content", "")
 
        if not path:
            return "Error: 'path' is required."
 
        # Auto-create parent directories
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
 
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
 
        return f"✅ File written successfully: {path}"
 
    except json.JSONDecodeError:
        return "Error: input must be valid JSON like {\"path\": \"file.txt\", \"content\": \"...\"}"
    except Exception as e:
        return f"Error writing file: {e}"
 

AVAILABLE_TOOLS = {
    "run_command": run_command,
    "write_file":  write_file, 
}


# ─────────────────────────────────────────────
# System Prompt
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a terminal automation agent. You MUST respond with ONLY a single valid JSON object.
No markdown, no explanation, no extra text — ONLY raw JSON.

Workflow: START → PLAN → TOOL (repeat if needed) → OUTPUT

JSON Schema (always include ALL four keys):
{
  "step": "START" | "PLAN" | "TOOL" | "OUTPUT",
  "content": "<what you are doing>",
  "tool": "<tool name or null>",
  "input": "<tool input string or null>"
}

Available Tools:
1. run_command
   - Runs a Windows shell command (cmd.exe).
   - Use for: creating folders (mkdir), listing files (dir), deleting files, etc.
   - Input: a plain shell command string.
   - Example: {"step":"TOOL","content":"Create folder","tool":"run_command","input":"mkdir my_app"}
   - ⚠️ NEVER use run_command with echo to write file content — use write_file instead.
 
2. write_file
   - Writes full content to a file. Creates parent folders automatically.
   - Use for: writing ANY file (HTML, CSS, JS, Python, JSON, etc.)
   - Input: a JSON string with "path" and "content" keys.
   - Example: {"step":"TOOL","content":"Write index.html","tool":"write_file","input":"{\"path\":\"my_app/index.html\",\"content\":\"<html>...</html>\"}"}
   - ✅ Always use this to write code — never use echo in run_command.

Rules:
- ONE JSON object per response, nothing else.
- Use null (not "None") for unused fields.
- After every TOOL step, wait for the OBSERVE message before continuing.
- You are on Windows — use Windows-compatible commands (mkdir, echo, type, etc.).
- Only emit OUTPUT when the task is fully complete.
"""


# ─────────────────────────────────────────────
# Grok Client Setup (OpenAI SDK)
# ─────────────────────────────────────────────

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"          # ✅ Grok (xAI) base URL
)


# ─────────────────────────────────────────────
# Helper: API call with retry on rate limit
# ─────────────────────────────────────────────

def call_api(messages, retries=5, wait=10):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",              # ✅ Grok model
                response_format={"type": "json_object"},
                temperature=0.2,            # lower = more reliable JSON
                messages=messages
            )
            return response
        except Exception as e:
            if "429" in str(e):
                print(f"⏳ Rate limited. Waiting {wait}s before retry ({attempt + 1}/{retries})...")
                time.sleep(wait)
            else:
                raise e
    raise Exception("❌ Max retries exceeded. Please wait a moment and try again.")


# ─────────────────────────────────────────────
# Main Agent Loop
# ─────────────────────────────────────────────

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

user_query = input("👉  ")
message_history.append({"role": "user", "content": user_query})

MAX_STEPS = 15

for step_num in range(MAX_STEPS):

    response = call_api(message_history)
    raw_result = response.choices[0].message.content

    # ── Safe JSON parse ────────────────────────────────────────────────────────
    try:
        parsed = json.loads(raw_result)
    except json.JSONDecodeError:
        print(f"⚠️  JSON parse error at step {step_num}. Raw output: {raw_result!r}")

        # Ask the model to self-correct
        message_history.append({
            "role": "user",
            "content": json.dumps({
                "step": "OBSERVE",
                "output": "ERROR: Your last response was not valid JSON. Return ONLY a single JSON object matching the schema, with no extra text."
            })
        })
        continue

    # Append valid assistant turn AFTER successful parse
    message_history.append({
        "role": "assistant",
        "content": raw_result
    })

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
            print(f"❌  {obs_output}")
        else:
            print(f"🛠️   {tool_name}({tool_input!r})")
            obs_output = AVAILABLE_TOOLS[tool_name](tool_input)
            print(f"📦  {obs_output}")

        # ✅ Send tool result back to model as "user" role
        message_history.append({
            "role": "user",
            "content": json.dumps({
                "step":   "OBSERVE",
                "tool":   tool_name,
                "input":  tool_input,
                "output": obs_output
            })
        })

    elif step == "OUTPUT":
        print(f"🤖  {content}")
        break

    else:
        print(f"⚠️  Unknown step '{step}' — raw: {raw_result!r}")
        break

else:
    print("⚠️  Reached max steps without OUTPUT.")

print("\n✅ Done.\n")