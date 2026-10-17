import os
import time

import gradio as gr

import beepy


def panel(child, seconds=0.0):
    return (f"**Mode:** {child['mode']}  \n"
            f"**Mood:** {child['mood']}  \n"
            f"**Level:** {child['level']} ({child['correct']} right in a row, {child['struggles']} struggles)  \n"
            f"**Learning turns in a row:** {child['streak']}  \n"
            f"**Mastered:** {', '.join(child['mastered']) or 'none yet'}  \n"
            f"**Practising:** {', '.join(child['struggling']) or 'none'}  \n"
            f"**Reply time:** {seconds:.2f} s")


def respond(message, name, age, likes, avoid, child):
    if not message.strip():
        return "", child["chat"], child, panel(child)
    profile = {
        "name": name.strip() or "friend",
        "age_years": int(age or 5),
        "native_language_hint": "Bangla",
        "favorite_topics": [t.strip() for t in likes.split(",") if t.strip()],
        "avoid_topics": [t.strip() for t in avoid.split(",") if t.strip()],
    }
    start = time.perf_counter()
    beepy.talk(child, profile, message)
    seconds = time.perf_counter() - start
    print(f"Reply time: {seconds:.2f} s | {child['mode']} | {child['mood']} | {child['level']}", flush=True)
    return "", child["chat"], child, panel(child, seconds)


with gr.Blocks(title="Beepy") as demo:
    gr.Markdown("# 🤖 Beepy: English fun for little learners")
    child = gr.State(beepy.new_child())
    with gr.Row():
        name = gr.Textbox(label="Child's name", placeholder="e.g. Ayaan")
        age = gr.Dropdown([3, 4, 5, 6], value=5, label="Age")
        likes = gr.Textbox(label="Favorite things", placeholder="e.g. dinosaurs, cars")
        avoid = gr.Textbox(label="Topics to avoid", placeholder="e.g. spiders, thunder")
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=450, placeholder="Say hi to Beepy! 👋")
            message = gr.Textbox(placeholder="Type here...", show_label=False)
        with gr.Column(scale=1):
            gr.Markdown("### 🔍 Behind the scenes")
            info = gr.Markdown("Say hi to start!")
    message.submit(respond, inputs=[message, name, age, likes, avoid, child],
                   outputs=[message, chatbot, child, info])

port = os.getenv("PORT")
if port:  # on Render
    demo.launch(server_name="0.0.0.0", server_port=int(port))
else:  # on your laptop
    demo.launch()