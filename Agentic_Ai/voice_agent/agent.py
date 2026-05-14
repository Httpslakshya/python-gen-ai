import speech_recognition as sr
from dotenv import load_dotenv
import os
from openai import OpenAI
import pyaudio
import wave
import io
from camb.client import CambAI
from camb.types import StreamTtsOutputConfiguration

load_dotenv()

camb_client = CambAI(api_key=os.getenv("CAMB_API_KEY"))
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ✅ speak() ab top-level pe hai, while loop ke bahar
def speak(text: str, voice_id: int = 147320):
    """Stream TTS audio directly to speakers — no file saved."""
    response = camb_client.text_to_speech.tts(
        text=text,
        voice_id=voice_id,
        language="hi-in",
        speech_model="mars-8.1-flash-beta",
        output_configuration=StreamTtsOutputConfiguration(format="wav")
    )

    # ✅ Sab kuch function ke andar sahi indentation ke saath
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


def main():
    r = sr.Recognizer()

    SYSTEM_PROMPT = """
    You are an expert voice agent. You are given the transcript of what 
    the user said using voice. Respond as a voice agent — your response 
    will be converted to audio and played back to the user.
    Keep responses short and conversational.
    """

  
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    with sr.Microphone(device_index=1) as source:
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 2

        while True:
            print("\nSpeak...")
            audio = r.listen(source)

            
            try:
                text = r.recognize_google(audio)
            except sr.UnknownValueError:
                print("Samajh nahi aaya, dobara bolo...")
                continue
            except sr.RequestError as e:
                print(f"STT Error: {e}")
                continue

            print(f"You: {text}")
            messages.append({"role": "user", "content": text})

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                messages=messages
            )

            llm_output = response.choices[0].message.content
            print(f"Agent: {llm_output}")

            # ✅ Assistant reply bhi history mein daalo — warna memory kaam nahi karegi
            messages.append({"role": "assistant", "content": llm_output})

            speak(llm_output)


main()