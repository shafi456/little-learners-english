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
MODEL = "openai/gpt-oss-20b"

PERSONA = """You are Beepy, a friendly little robot who helps a child under 7 learn English.
Use very simple English: short sentences and easy words, with 1 or 2 fun emojis.
Be kind and patient. Praise effort. Never say "wrong".
If you don't understand a word the child wrote, don't guess what it means.
Never ask for personal details like an address, school name or phone number.
Do not use markdown."""


def ask_ai(facts, task, allow_question=False):
    """Ask the AI for a short, warm reply. Returns None if it fails or breaks a rule."""
    rule = "You may end with ONE simple question." if allow_question else "Do not ask a question."
    messages = [
        {"role": "system", "content": PERSONA},
        {"role": "user", "content": f"{facts}\n\nYour job: {task} {rule}"},
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
    reply = " ".join(text.split())  # one tidy line
    max_questions = 1 if allow_question else 0
    if not reply or reply.count("?") > max_questions or len(reply) > 250:
        print("AI broke a rule, using backup:", text, flush=True)
        return None
    return reply