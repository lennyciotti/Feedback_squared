from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("✅ OpenAI API key is loaded!")
else:
    print("❌ OpenAI API key NOT loaded.")