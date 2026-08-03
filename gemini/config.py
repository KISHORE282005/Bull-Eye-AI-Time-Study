import os
import truststore
truststore.inject_into_ssl()

from dotenv import load_dotenv
from google import genai
from google.genai import types

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

MODEL = "gemini-3.6-flash"

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(
        timeout=900_000  # 15 minutes (milliseconds) — video analysis is slow
    )
)