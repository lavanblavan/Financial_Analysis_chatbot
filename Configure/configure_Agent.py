from dotenv import load_dotenv
import os

load_dotenv()

Groq_api = os.getenv("Groq_api")
if not Groq_api:
    raise ValueError("Groq_api is not set in the environment variables.")
tavily_api = os.getenv("Tavily_api")
if not tavily_api:
    raise ValueError("Tavily_api is not set in the environment variables.")

