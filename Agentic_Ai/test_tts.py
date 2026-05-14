import os
from elevenlabs.client import ElevenLabs

# ElevenLabs requires an API key even for the free tier (10,000 characters/month limit)
api_key = os.getenv("ELEVENLABS_API_KEY", "")

if not api_key:
    print("WARNING: ELEVENLABS_API_KEY is not set. The ElevenLabs API requires a key even for the free tier.")
    print("You can get a free API key at https://elevenlabs.io/")
    print("Continuing without key (this will likely fail with a 401 Unauthorized error)...")

try:
    client = ElevenLabs(api_key=api_key)
    print("\n[+] Testing ElevenLabs Text-to-Speech API...")
    
    # We will just generate a small string to test
    audio = client.generate(
      text="Hello! This is a test of the ElevenLabs Text-to-Speech API.",
      voice="Rachel",
      model="eleven_multilingual_v2"
    )
    
    with open("elevenlabs_output.mp3", "wb") as f:
        for chunk in audio:
            f.write(chunk)
    print("Success! Audio saved to elevenlabs_output.mp3")

except Exception as e:
    print(f"ElevenLabs API Error: {e}")

print("\n[+] As an alternative, here is how you can use Edge TTS (completely free, no API key):")
print("Run this command in terminal:")
print("pip install edge-tts")
print("edge-tts --text 'Hello, this is Edge TTS' --write-media edge_tts_output.mp3")
