"""beepy.py: talks to the AI and keeps score. All behaviour lives in prompt.md."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    timeout=5,
    max_retries=0,
)
MODEL = "openai/gpt-oss-120b"
PROMPT = (Path(__file__).parent / "prompt.md").read_text(encoding="utf-8")
LEVELS = ["L1", "L2", "L3"]


def new_child():
    return {"level": "L1", "correct": 0, "struggles": 0, "streak": 0, "turn": 0, "mode": None,
            "mood": "unknown", "mastered": [], "struggling": [], "history": [], "chat": []}


def runtime_context(child, profile):
    """Everything the code knows for sure, in the RUNTIME_CONTEXT shape the prompt expects."""
    return {
        "child_profile": profile,
        "learning_state": {
            "current_level": child["level"],
            "consecutive_correct_attempts": child["correct"],
            "consecutive_struggles": child["struggles"],
            "mastered_vocabulary": child["mastered"][-10:],
            "struggling_vocabulary": child["struggling"][-5:],
            "turns_in_learning_mode_streak": child["streak"],
        },
        "session_context": {
            "previous_mode": child["mode"],
            "detected_child_mood": child["mood"],
            "turn_number": child["turn"] + 1,
        },
    }


def read_state(text):
    """Turn the JSON after |||STATE||| into a dictionary. Returns {} if it's missing or broken."""
    try:
        return json.loads(text[text.find("{"): text.rfind("}") + 1])
    except ValueError:
        return {}


def update(child, state):
    """Keep score from the AI's notes. Stepping down is easy; stepping up needs 3 right in a row."""
    child["mode"] = state.get("mode", child["mode"])
    child["mood"] = state.get("detected_mood", child["mood"])
    child["streak"] = child["streak"] + 1 if child["mode"] == "LEARNING" else 0

    word, status = state.get("target_word_practiced"), state.get("word_status")
    if status in ("practiced", "mastered"):
        child["correct"], child["struggles"] = child["correct"] + 1, 0
    elif status == "struggled":
        child["correct"], child["struggles"] = 0, child["struggles"] + 1
    if word and status == "mastered" and word not in child["mastered"]:
        child["mastered"].append(word)
        if word in child["struggling"]:
            child["struggling"].remove(word)
    elif word and status == "struggled" and word not in child["struggling"]:
        child["struggling"].append(word)

    level = LEVELS.index(child["level"])
    if state.get("level_action") == "step_up" and child["correct"] >= 3 and level < 2:
        child["level"], child["correct"] = LEVELS[level + 1], 0
    elif state.get("level_action") == "step_down" and level > 0:
        child["level"], child["struggles"] = LEVELS[level - 1], 0


def talk(child, profile, message):
    """One turn: send the prompt, the recent chat and the child's state; read back Beepy's words and notes."""
    context = json.dumps(runtime_context(child, profile), ensure_ascii=False)
    messages = [{"role": "system", "content": PROMPT}]  # identical every time, so Groq can cache it
    messages += child["history"][-8:]  # the last 4 exchanges
    messages.append({"role": "user", "content": f"[RUNTIME_CONTEXT]\n{context}\n\n[CHILD SAYS]\n{message}"})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_completion_tokens=1000,
            extra_body={"reasoning_effort": "low"},
        )
        raw = response.choices[0].message.content or ""
    except RateLimitError:
        raw = "Beepy needs a tiny rest. Let's play again in a minute!"
    except Exception as error:
        print("AI problem:", error, flush=True)
        raw = "Oops! Can you say that again?"

    spoken, _, notes = raw.partition("|||STATE|||")
    spoken = spoken.replace("```text", "").replace("```", "").strip()
    state = read_state(notes)
    if state:  # only remember replies that followed the format, so the AI keeps following it
        update(child, state)
        child["history"] += [{"role": "user", "content": message}, {"role": "assistant", "content": raw}]
    child["turn"] += 1
    child["chat"] += [{"role": "user", "content": message}, {"role": "assistant", "content": spoken}]
    return spoken