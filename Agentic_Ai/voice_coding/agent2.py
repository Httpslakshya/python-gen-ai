import asyncio
import speech_recognition as sr
from dotenv import load_dotenv
import os
import json
import requests
import httpx
import pyaudio
import wave
import io
from camb.client import CambAI
from camb.types import StreamTtsOutputConfiguration

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
camb_client = CambAI(api_key=os.getenv("CAMB_API_KEY"))

SENTENCE_ENDERS = {'.', '?', '!', '।', '…'}

# ============================================================
# TOOLS
# ============================================================

def weather(city: str):
    url = f"http://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"Current weather in {city} is: {response.text}"
    return "Unable to get weather data"


def create_file(input_str: str):
    """
    input_str format: "filename.py|||actual code content"
    Supports nested paths like: "weather/index.html|||<html>...</html>"
    """
    try:
        if "|||" in input_str:
            filename, content = input_str.split("|||", 1)
            filename = filename.strip()
            content = content.strip()
        else:
            return "Error: input format should be 'filename|||code content'"

        # Create parent directories if needed (e.g., weather/index.html)
        parent_dir = os.path.dirname(filename)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return f"File '{filename}' successfully created with {len(content.splitlines())} lines of code."

    except Exception as e:
        return f"Error creating file: {str(e)}"


def create_folder(folder_name: str):
    """Creates a folder in the current directory."""
    try:
        os.makedirs(folder_name, exist_ok=True)
        return f"Folder '{folder_name}' created successfully."
    except Exception as e:
        return f"Error creating folder: {str(e)}"


available_tools = {
    "weather": weather,
    "create_file": create_file,
    "create_folder": create_folder,
}

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an expert AI voice agent resolving user queries using chain of thought method.
You work on START, PLAN, TOOL, OBSERVE and OUTPUT steps.

Rules:
- Strictly follow the given JSON output format.
- Only one step at a time.
- Sequence: START → PLAN (multiple) → TOOL (if needed) → OBSERVE → OUTPUT
- OUTPUT content will be spoken aloud — keep it SHORT, natural, conversational.
- OUTPUT must NEVER contain code, file contents, or long text.
- If you created files, just say "Files created successfully" in OUTPUT.
- No markdown, no bullet points in OUTPUT.
- When creating multiple files, use multiple TOOL steps one by one.
- For nested files like weather/index.html, use that as the filename directly in create_file.

Code Quality Rules (VERY IMPORTANT):
- When writing HTML/CSS/JS code, write COMPLETE, FULL, PRODUCTION-QUALITY code.
- NEVER write placeholder or skeleton code — always write the real working implementation.
- CSS must have beautiful modern styling: gradients, shadows, animations, hover effects, responsive design.
- HTML must be complete with proper meta tags, linked CSS and JS files.
- JS must be fully functional with all features working.
- Do NOT truncate or shorten code under any circumstances.
- Write at minimum 50-100 lines per file for any UI project.
Output JSON Format:
{"step": "START" | "PLAN" | "TOOL" | "OBSERVE" | "OUTPUT", "content": "string", "tool": "string", "input": "string"}

Available Tools:
- weather(city): takes city name, returns weather info
- create_folder(folder_name): creates a folder in current directory
- create_file(input): creates a file. Input format MUST be "filepath|||file_content"
  - filepath can include folder: "weather/index.html|||<html>...</html>"

Example 1 — Weather:
{"step":"PLAN","content":"User wants weather for Delhi, I have weather tool"}
{"step":"TOOL","tool":"weather","input":"delhi"}
{"step":"OBSERVE","tool":"weather","output":"haze 20C"}
{"step":"OUTPUT","content":"Delhi is currently hazy with 20 degrees temperature."}

Example 2 — Create Folder + Files:
{"step":"PLAN","content":"User wants a weather app folder with HTML, CSS, JS files"}
{"step":"PLAN","content":"First create the folder, then create each file one by one"}
{"step":"TOOL","tool":"create_folder","input":"weather"}
{"step":"OBSERVE","tool":"create_folder","output":"Folder 'weather' created successfully."}
{"step":"TOOL","tool":"create_file","input":"weather/index.html|||<!DOCTYPE html><html>...</html>"}
{"step":"OBSERVE","tool":"create_file","output":"File 'weather/index.html' successfully created"}
{"step":"TOOL","tool":"create_file","input":"weather/style.css|||body { margin: 0; }"}
{"step":"OBSERVE","tool":"create_file","output":"File 'weather/style.css' successfully created"}
{"step":"TOOL","tool":"create_file","input":"weather/script.js|||console.log('hello')"}
{"step":"OBSERVE","tool":"create_file","output":"File 'weather/script.js' successfully created"}
{"step":"OUTPUT","content":"Done! Weather app folder with HTML, CSS, and JavaScript files has been created."}
"""

# ============================================================
# TTS
# ============================================================

def speak_sync(text: str, voice_id: int = 147320):
    if not text.strip():
        return
    try:
        response = camb_client.text_to_speech.tts(
            text=text,
            voice_id=voice_id,
            language="hi-in",
            speech_model="mars-8.1-flash-beta",
            output_configuration=StreamTtsOutputConfiguration(format="wav")
        )
        audio_buffer = io.BytesIO()
        for chunk in response:
            audio_buffer.write(chunk)
        audio_buffer.seek(0)

        with wave.open(audio_buffer, 'rb') as wf:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
            chunk_size = 1024
            data = wf.readframes(chunk_size)
            while data:
                stream.write(data)
                data = wf.readframes(chunk_size)
            stream.stop_stream()
            stream.close()
            p.terminate()

    except Exception as e:
        print(f"⚠️ TTS Error (skipping): {e}")


async def speak(text: str):
    if len(text) > 200:
        text = text[:200]
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, speak_sync, text)
    except asyncio.CancelledError:
        print("⚠️ Speak cancelled")


async def speak_streaming(text: str):
    if len(text) > 300:
        print("⚠️ Output too long for TTS, truncating...")
        text = text[:300]

    tts_queue = asyncio.Queue()

    async def producer():
        sentence_buffer = ""
        for char in text:
            sentence_buffer += char
            if any(sentence_buffer.rstrip().endswith(p) for p in SENTENCE_ENDERS):
                await tts_queue.put(sentence_buffer.strip())
                sentence_buffer = ""
        if sentence_buffer.strip():
            await tts_queue.put(sentence_buffer.strip())
        await tts_queue.put(None)

    async def consumer():
        while True:
            try:
                sentence = await tts_queue.get()
                if sentence is None:
                    break
                await speak(sentence)
            except asyncio.CancelledError:
                break

    try:
        await asyncio.gather(producer(), consumer())
    except asyncio.CancelledError:
        print("⚠️ speak_streaming cancelled")


# ============================================================
# STT
# ============================================================

async def listen_async(r: sr.Recognizer, source) -> str | None:
    loop = asyncio.get_event_loop()
    try:
        print("\n🎙️  Speak...")
        audio = await loop.run_in_executor(None, lambda: r.listen(source))
        text = await loop.run_in_executor(
            None, lambda: r.recognize_google(audio, language="hi-IN")
        )
        return text
    except sr.UnknownValueError:
        print("Samajh nahi aaya, dobara bolo...")
        return None
    except sr.RequestError as e:
        print(f"STT Error: {e}")
        return None


# ============================================================
# API CALL — freemodel.dev /v1/responses
# ============================================================

async def call_llm(message_history: list) -> str:
    async with httpx.AsyncClient(timeout=120) as http:   # ← timeout bhi badha do
        resp = await http.post(
            "https://api.freemodel.dev/v1/responses",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            json={
                "model": "gpt-5.5",
                "instructions": SYSTEM_PROMPT,
                "input": json.dumps(message_history),
                "max_output_tokens": 4096,              # ← ADD THIS
                "text": {"format": {"type": "json_object"}}
            }
        )
        if resp.status_code != 200:
            print(f"❌ API Error {resp.status_code}: {resp.text}")
            raise Exception(f"API returned {resp.status_code}: {resp.text}")

        data = resp.json()
        return data["output"][0]["content"][0]["text"]


# ============================================================
# COT AGENT LOOP
# ============================================================

async def run_cot_agent(user_query: str, message_history: list) -> str:
    message_history.append({"role": "user", "content": user_query})

    while True:
        try:
            raw_result = await call_llm(message_history)
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return "Kuch error aa gaya, dobara try karo."

        try:
            parsed_result = json.loads(raw_result)
        except json.JSONDecodeError:
            print("⚠️ JSON Error:", raw_result)
            return "Kuch error aa gaya, dobara try karo."

        message_history.append({"role": "assistant", "content": raw_result})

        step = parsed_result.get("step")
        content = parsed_result.get("content", "")

        if step == "START":
            print(f"🔥 START: {content}")
            continue

        elif step == "PLAN":
            print(f"🧠 PLAN: {content}")
            continue

        elif step == "TOOL":
            tool_name = parsed_result.get("tool")
            tool_input = parsed_result.get("input")
            display_input = (tool_input[:80] + "...") if tool_input and len(tool_input) > 80 else tool_input
            print(f"🔧 TOOL: {tool_name}({display_input})")

            if tool_name not in available_tools:
                tool_response = f"Tool '{tool_name}' not found. Available: {list(available_tools.keys())}"
            else:
                loop = asyncio.get_event_loop()
                tool_response = await loop.run_in_executor(
                    None, available_tools[tool_name], tool_input
                )

            print(f"👁️  OBSERVE: {tool_response}")
            message_history.append({
                "role": "user",
                "content": json.dumps({
                    "step": "OBSERVE",
                    "tool": tool_name,
                    "input": tool_input,
                    "output": tool_response
                })
            })
            continue

        elif step == "OUTPUT":
            print(f"🤖 OUTPUT: {content}")
            return content


# ============================================================
# MAIN
# ============================================================

async def main():
    r = sr.Recognizer()
    message_history = []

    await speak("Namaste! Main aapki madad karne ke liye yahaan hoon.")

    with sr.Microphone(device_index=1) as source:
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 2

        while True:
            user_text = await listen_async(r, source)
            if not user_text:
                continue

            print(f"👤 You: {user_text}")

            output = await run_cot_agent(user_text, message_history)
            message_history.append({"role": "assistant", "content": output})

            await speak_streaming(output)


asyncio.run(main())