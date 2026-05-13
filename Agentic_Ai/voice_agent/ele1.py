import os
from dotenv import load_dotenv
from camb.client import CambAI, save_stream_to_file
from camb.types import StreamTtsOutputConfiguration

load_dotenv()
api_key=os.getenv("CAMB_API_KEY")
client = CambAI(api_key=api_key)
# Generate speech and save to file
response = client.text_to_speech.tts(
    text="Namaste Lakshya, mera naam Voice Agent hai. Main aapki madad karne ke liye yahaan hoon. Aaj main aapki kya madad kar sakta hoon?",
    voice_id=147320,
    language="hi-in",
    speech_model="mars-8.1-flash-beta",
    output_configuration=StreamTtsOutputConfiguration(format="wav")
)

save_stream_to_file(response, "output.wav")
print("Audio saved to output.wav")