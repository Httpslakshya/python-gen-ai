import asyncio
import speech_recognition as sr
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os
import json
import requests
import pyaudio
import wave
import io
from camb.client import CambAI
from camb.types import StreamTtsOutputConfiguration

load_dotenv()

camb_client = CambAI(api_key=os.getenv("CAMB_API_KEY"))
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

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


# ✅ NEW TOOL — file create karo
def create_file(input_str: str):
    """
    input_str format: "filename.py|||actual code content"
    """
    try:
        # ✅ LLM "filename|||content" format mein dega
        if "|||" in input_str:
            filename, content = input_str.split("|||", 1)
            filename = filename.strip()
            content = content.strip()
        else:
            return "Error: input format should be 'filename|||code content'"

        # ✅ File create karo current directory mein
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return f"File '{filename}' successfully created with {len(content.splitlines())} lines of code."

    except Exception as e:
        return f"Error creating file: {str(e)}"


available_tools = {
    "weather": weather,
    "create_file": create_file,   # ✅ Registered
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
- If you created a file, just say "File created successfully" in OUTPUT.
- No markdown, no bullet points in OUTPUT.

Output JSON Format:
{"step": "START" | "PLAN" | "TOOL" | "OBSERVE" | "OUTPUT", "content": "string", "tool": "string", "input": "string"}

Available Tools:
- weather(city): takes city name, returns weather info
- create_file(input): creates a file. Input format MUST be "filename|||code_content"

Example 1 — Weather:
{"step":"PLAN","content":"User wants weather for Delhi, I have weather tool"}
{"step":"TOOL","tool":"weather","input":"delhi"}
{"step":"OBSERVE","tool":"weather","output":"haze 20C"}
{"step":"OUTPUT","content":"Delhi is currently hazy with 20 degrees temperature."}

Example 2 — Create File:
{"step":"PLAN","content":"User wants a calculator Python file created"}
{"step":"PLAN","content":"I will write the code and use create_file tool"}
{"step":"TOOL","tool":"create_file","input":"calculator.py|||def add(a,b):\\n    return a+b\\nprint(add(2,3))"}
{"step":"OBSERVE","tool":"create_file","output":"File 'calculator.py' successfully created"}
{"step":"OUTPUT","content":"Done! Calculator file has been created in the current folder."}
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

    # ✅ TTS crash ho toh silently handle karo
    except Exception as e:
        print(f"⚠️ TTS Error (skipping): {e}")


async def speak(text: str):
    # ✅ 200 char se zyada ho toh truncate — TTS crash nahi karega
    if len(text) > 200:
        text = text[:200]
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, speak_sync, text)
    except asyncio.CancelledError:
        print("⚠️ Speak cancelled")


async def speak_streaming(text: str):
    # ✅ Code ya long text TTS mein mat bhejo
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
# COT AGENT LOOP
# ============================================================

async def run_cot_agent(user_query: str, message_history: list) -> str:
    message_history.append({"role": "user", "content": user_query})

    while True:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=message_history
        )

        raw_result = response.choices[0].message.content

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
            print(f"🔧 TOOL: {tool_name}({tool_input[:80]}...)" if tool_input and len(tool_input) > 80 else f"🔧 TOOL: {tool_name}({tool_input})")

            if tool_name not in available_tools:
                tool_response = f"Tool '{tool_name}' not found. Available tools: {list(available_tools.keys())}"
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
    message_history = [{"role": "system", "content": SYSTEM_PROMPT}]

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