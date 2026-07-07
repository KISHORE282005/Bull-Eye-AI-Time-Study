import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# ==========================================
# CONFIGURATION
# ==========================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable not set. "
        "Copy .env.example to .env and add your API key."
    )

MODEL = "gemini-2.5-flash"

client = genai.Client(
    api_key=API_KEY
)