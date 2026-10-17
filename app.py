import os
import time

import gradio as gr
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

SYSTEM_PROMPT = """You are Beepy, a friendly little robot who 
helps a child under 7 learn English.
Use very simple English: short sentences and easy words. 
Reply in 1 or 2 short sentences, with 1 or 2 fun emojis.
Be kind and patient. Praise effort. Never say "wrong".
Never ask for personal details like an address, school name
or phone number."""


def ask_buddy(history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history[-6:]
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_completion_tokens=400,
            extra_body={"reasoning_effort": "low"},
        )
        return response.choices[0].message.content or "Hmm, let me think again! 🤔"
    except Exception as error:
        print("AI problem", error)
        return "Oops! Let's try that again. 🌈"


def respond(message, history):
    if not message.strip():
        return "", history, history
    start = time.perf_counter()
    history = history + [{"role": "user", "content": message}]
    reply = ask_buddy(history)
    history = history + [{"role": "assistant", "content": reply}]
    print(f"Reply time: {time.perf_counter() - start:.2f} s")
    return "", history, history


with gr.Blocks(title="Beepy") as demo:
    gr.Markdown("# 🌈 Beepy: English fun for little learners")
    history = gr.State([])
    chatbot = gr.Chatbot(height=450)
    message = gr.Textbox(placeholder="Type here...", show_label=False)
    message.submit(respond, inputs=[message, history], outputs=[message, chatbot, history])

port = os.getenv("PORT")
if port:
    demo.launch(server_name="0.0.0.0", server_port=int(port))
else:
    demo.launch()