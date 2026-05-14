import os
import pyaudio
import wave
import io
from dotenv import load_dotenv
from camb.client import CambAI
from camb.types import StreamTtsOutputConfiguration

load_dotenv()
api_key = os.getenv("CAMB_API_KEY")
client = CambAI(api_key=api_key)

def speak(text: str, voice_id: int = 147320):
    """Stream TTS audio directly to speakers — no file saved."""
    response = client.text_to_speech.tts(
        text=text,
        voice_id=voice_id,
        language="hi-in",
        speech_model="mars-8.1-flash-beta",
        output_configuration=StreamTtsOutputConfiguration(format="wav")
    )

    # Collect the stream into a buffer
    audio_buffer = io.BytesIO()
    for chunk in response:
        audio_buffer.write(chunk)
    audio_buffer.seek(0)

    # Parse WAV headers and play via PyAudio
    with wave.open(audio_buffer, 'rb') as wf:
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )

        # Play in chunks for low latency
        chunk_size = 1024
        data = wf.readframes(chunk_size)
        while data:
            stream.write(data)
            data = wf.readframes(chunk_size)

        stream.stop_stream()
        stream.close()
        p.terminate()


# Test
speak("Namaste Lakshya, mera naam Voice Agent hai. Aaj main aapki kya madad kar sakta hoon?")