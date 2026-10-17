"""ai.py: the only file that talks to the AI model."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    timeout=5,
    max_retries=0,
)
MODEL = "openai/gpt-oss-120b"

PERSONA = """You are Beepy, a friendly little robot who helps a child under 7 learn English.
Use very simple English: short sentences and easy words, with 1 or 2 fun emojis.
Be kind and patient. Praise effort. Never say "wrong".
Never ask for personal details like an address, school name or phone number.
Do not use markdown."""


def ask_ai(facts, task):
    """Ask the AI for ONE warm sentence. Returns None if it fails or breaks a rule."""
    messages = [
        {"role": "system", "content": PERSONA},
        {"role": "user", "content": f"{facts}\n\nYour job: {task} Write only ONE short sentence. Do not ask a question."},
    ]
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_completion_tokens=400,
            extra_body={"reasoning_effort": "low"},
        )
        text = (response.choices[0].message.content or "").strip()
    except Exception as error:
        print("AI problem:", error, flush=True)
        return None
    line = text.split("\n")[0].strip()
    if not line or "?" in line:  # safety net: only the code asks questions
        print("AI broke a rule, using backup:", text, flush=True)
        return None
    return line