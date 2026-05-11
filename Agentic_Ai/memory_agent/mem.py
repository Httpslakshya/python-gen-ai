from mem0 import Memory
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dims": 384
        }
    },
    "llm": {
        "provider": "groq",
        "config": {"api_key": api_key, "model": "llama-3.3-70b-versatile"}
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "lakshya_memory",
            "embedding_model_dims": 384
        }
    }
}

mem_client = Memory.from_config(config)

print("🧠 Memory Agent Ready! (type 'exit' to quit)\n")

while True:
    user_query = input("👱 : ").strip()  # .strip() removes whitespace

    # ✅ FIX 1: Empty input check - Enter press karne par skip karo
    if not user_query:
        print("⚠️  Kuch toh likhो!\n")
        continue

    # ✅ Exit command
    if user_query.lower() in ["exit", "quit", "bye"]:
        print("👋 Bye!")
        break

    # Memory search
    search_memory = mem_client.search(
        query=user_query,
        filters={"user_id": "lakshyadharkar"}
    )

    memories = [
        f"ID: {mem.get('id')}\nMemory: {mem.get('memory')}"
        for mem in search_memory.get("results", [])
    ]

    SYSTEM_PROMPT = f"""You are a personal AI assistant
                        MEMORIES (sorted newest first, prefer recent over old):
                         context:
                           {json.dumps(memories, indent=2)}
                        RULES:
                            - If two memories contradict, always trust the MORE RECENT one
                            - If unsure, ask the user to confirm
                            - Never mention memory IDs or multiple users
 """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ]
        )
        ai_response = response.choices[0].message.content
        print(f"🤖: {ai_response}\n")

        # ✅ FIX 2: Memory save bhi try-except mein
        try:
            mem_client.add(
                user_id="lakshyadharkar",
                messages=[
                    {"role": "user", "content": user_query},
                    {"role": "assistant", "content": ai_response}
                ]
            )
            print("✅ Memory saved\n")
        except Exception as mem_err:
            print(f"⚠️  Memory save failed: {mem_err}\n")

    # ✅ FIX 3: Rate limit handle karo gracefully
    except Exception as e:
        error_msg = str(e)
        if "rate_limit_exceeded" in error_msg or "429" in error_msg:
            print("⏳ Groq rate limit hit! Thodi der baad try karo.\n")
        else:
            print(f"❌ Error: {e}\n")