import speech_recognition as sr
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()


client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"        
)
def main():
    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:

        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 2
        print("Speak...")
    
        audio = r.listen(source)

        text = r.recognize_google(audio)

        print(text)

        SYSTEM_PROMPT=f"""
        you're an expert voice agent .you are given the transcript of what user said uising voice
        you need to output as if you are an voice agent and whatever you speak will be converted back to 
        audio using AI and played back to user.

        """
        response=client.chat.completions.create(
                model="llama-3.3-70b-versatile",             
                
                temperature=0.2,            # lower = more reliable JSON
                messages=[
                    {"role":"system", "content":SYSTEM_PROMPT },
                    {"role":"user", "content":text },
                ]
            )
        print(f"🤖: {response.choices[0].message.content}")


main()
