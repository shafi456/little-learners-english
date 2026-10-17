"""tutor.py: Beepy's brain. Rules decide WHAT happens; the AI only decides HOW to say it."""

import lessons
from ai import ask_ai


def new_child():
    return {"level": 1, "question": None, "tries": 0, "recent": [], "done": [], "history": []}


def say(facts, task, backup):
    """The AI writes one warm sentence from the facts. If it fails or breaks a rule, use the backup."""
    return ask_ai(facts, task) or backup


def handle(child, message):
    """One turn of the chat. The child said `message`; returns Beepy's reply."""
    child["history"].append({"role": "user", "content": message})
    question = child["question"]

    if question is None:  # first message: say hello, then ask the first question
        reply = say(f'The child said: "{message}". This is the start of the lesson.',
                    "Greet the child warmly.", "Hi! I'm Beepy, your robot friend! 🤖")
        reply += "\n\n" + next_question(child)

    elif lessons.check_answer(question, message):  # right answer
        child["done"].append(question["q"])
        if record(child, True):
            reply = say(f'The child answered "{message}" correctly and just reached Level {child["level"]} of 3!',
                        "Celebrate the new level.", f"🎉 Hooray! You reached Level {child['level']}!")
        else:
            reply = say(f'Beepy asked: "{question["q"]}". The child answered: "{message}". That is RIGHT.',
                        "Cheer for the child.", "Yay! You got it! 🎉")
        reply += "\n\n" + next_question(child)

    elif child["tries"] == 0:  # first wrong try: encourage, give a hint, same question
        child["tries"] = 1
        reply = say(f'Beepy asked: "{question["q"]}". The child answered: "{message}". That is not right yet.',
                    "Encourage them to try again. Do NOT say the answer.", "Good try! 💪")
        reply += "\n\n💡 Hint: " + question["hint"]

    else:  # second wrong try: show the answer kindly, then move on
        record(child, False)
        reply = f"The answer is: {question['show']} ✨\n\n"
        reply += say(f'The child tried twice but could not answer: "{question["q"]}".',
                     "Say kindly that trying hard makes our brain grow.", "Trying hard makes your brain grow! 🧠")
        reply += "\n\n" + next_question(child)

    child["history"].append({"role": "assistant", "content": reply})
    return reply


def next_question(child):
    child["question"] = lessons.pick_question(child["level"], child["done"], child["question"])
    child["tries"] = 0
    return child["question"]["q"]


def record(child, correct):
    """Keep the last 5 results. 4 right out of 5 means the next level. Returns True on a level up."""
    child["recent"] = (child["recent"] + [correct])[-5:]
    if sum(child["recent"]) >= 4 and child["level"] < 3:
        child["level"] += 1
        child["recent"] = []
        return True
    return False