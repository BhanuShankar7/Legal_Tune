
import requests
import json
import logging
import sys
from config import GEMINI_API_KEY

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Try gemini-2.5-flash
URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
API_KEY = GEMINI_API_KEY

print(f"DEBUG: Testing Model: {URL.split('/')[-1]}")

system_instructions = "You are a Legal Information Assistant."
prompt_text = "Explain IPC 420"
full_text = f"{system_instructions}\n\n{prompt_text}"

payload = {
    "contents": [
        {
            "parts": [{"text": full_text}]
        }
    ]
}

print("DEBUG: Sending Request...")
try:
    response = requests.post(f"{URL}?key={API_KEY}", json=payload, timeout=30)
    print(f"DEBUG: Status: {response.status_code}")
    print(f"DEBUG: Response head: {response.text[:200]}")
    
    if response.status_code == 200:
        print("SUCCESS! Model is available.")
    else:
        print("FAILURE. Model not usable.")

except Exception as e:
    print(f"DEBUG: Error: {e}")
