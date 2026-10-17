import os
import time

import gradio as gr

import tutor


def respond(message, child):
    if not message.strip():
        return "", child["history"], child
    start = time.perf_counter()
    tutor.handle(child, message)
    print(f"Reply time: {time.perf_counter() - start:.2f} s", flush=True)
    return "", child["history"], child


with gr.Blocks(title="Beepy") as demo:
    gr.Markdown("# 🤖 Beepy: English fun for little learners")
    child = gr.State(tutor.new_child())
    chatbot = gr.Chatbot(height=450, placeholder="Say hi to Beepy! 👋")
    message = gr.Textbox(placeholder="Type here...", show_label=False)
    message.submit(respond, inputs=[message, child], outputs=[message, chatbot, child])

port = os.getenv("PORT")
if port:  
    demo.launch(server_name="0.0.0.0", server_port=int(port))
else:  
    demo.launch()