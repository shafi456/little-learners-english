"""tutor.py: Beepy's brain. Rules decide WHAT happens; the AI only decides HOW to say it."""

import lessons
import modes
from ai import ask_ai

# Social-emotional learning: a calming idea for each feeling (idea for the AI, ready-made backup).
CALM = {
    "sad": ("Offer a big hug emoji and say it is okay to feel sad sometimes.",
            "I'm sorry you feel sad. 💛 It's okay to feel sad sometimes. Here's a big hug! 🤗 "
            "Do you want a game or a new word?"),
    "angry": ("Do a balloon breath together: breathe in slowly, then blow out.",
              "It's okay to feel angry. 💛 Let's do a balloon breath: breathe in... and blow out! 🎈 "
              "Do you want a game or a new word?"),
    "scared": ("Say they are safe here, then do a slow balloon breath together.",
               "You are safe here with me. 💛 Let's breathe in slowly... and out. 🎈 "
               "Do you want a game or a new word?"),
    "tired": ("Suggest a quick stretch: reach up tall like a tree.",
              "You worked so hard! 💛 Let's stretch up tall like a tree! 🌳 Do you want a rest, a game or a new word?"),
    "frustrated": ("Say that tricky things help our brain grow, then do a balloon breath together.",
                   "Tricky things help our brain grow! 🧠💛 Let's take a balloon breath together. 🎈 "
                   "Do you want a game or a new word?"),
}

# Quick games for engagement mode (idea for the AI, ready-made backup).
GAMES = [
    ("Ask a very easy animal riddle, like: I say moo, who am I?", "Riddle time! 🐄 I say moo. Who am I?"),
    ("Play I Spy with three emojis, like: I spy something yellow! 🍌🚗🐸", "I spy something yellow! 🍌🚗🐸 What is it?"),
    ("Ask the child to do a fun action and type the word, like: jump like a frog, then type jump!",
     "Let's move! 🐸 Jump like a frog, then type: jump!"),
    ("Tell a two-sentence story about a cute animal and ask one easy question about it.",
     "Story time! 🐱 A little cat found a red ball. What color was the ball?"),
]


def new_child():
    return {"level": 1, "question": None, "tries": 0, "recent": [], "done": [], "history": [],
            "mode": "hello", "mode_turns": 0, "reason": "new chat", "mood": "unknown", "streak": 0, "games": 0}


def say(facts, task, backup, allow_question=False):
    """The AI writes the warm words from the facts. If it fails or breaks a rule, use the backup."""
    return ask_ai(facts, task, allow_question) or backup


def switch(child, mode, reason):
    """Move to a new mode and remember why (handy for testing, and for the panel in Session 4)."""
    if mode != child["mode"]:
        child["mode"], child["mode_turns"] = mode, 0
    if mode != "learning":
        child["streak"] = 0
    child["reason"] = reason


def last_beepy(child):
    """Beepy's previous message, so the AI knows what the child is replying to."""
    return child["history"][-2]["content"] if len(child["history"]) >= 2 else ""


def handle(child, message):
    """One turn of the chat. The child said `message`; returns Beepy's reply."""
    child["history"].append({"role": "user", "content": message})
    question = child["question"]

    if child["mode"] == "hello":
        reply = hello(child, message)
    elif child["mode"] == "learning" and question and lessons.check_answer(question, message):
        reply = right_answer(child, question, message)  # a right answer always counts first
    else:
        mood = modes.detect_mood(message)
        if mood:
            child["mood"] = mood
        mode, reason = modes.choose_mode(child, message, mood)
        if mode == "learning" and child["mode"] == "learning" and question:
            reply = wrong_answer(child, question, message)  # it was a try at the question
        else:
            switch(child, mode, reason)
            if mode == "support":
                reply = support(child, message)
            elif mode == "engagement":
                reply = game(child, message)
            elif mode == "conversation":
                reply = chat(child, message)
            else:
                reply = lesson(child, message)

    child["mode_turns"] += 1
    child["history"].append({"role": "assistant", "content": reply})
    return reply


def hello(child, message):
    """First message: greet, then check in on feelings."""
    switch(child, "checkin", "asking how the child feels")
    text = say(f'The child said: "{message}". This is the start of the chat.',
               "Greet the child warmly in ONE short sentence.", "Hi! I'm Beepy, your robot friend! 🤖")
    return text + "\n\nHow do you feel today? Happy 😊, sad 😢 or sleepy 😴?"


def lesson(child, message):
    """Back to learning: react kindly to what the child said, then ask the question."""
    if child["question"] is None:
        next_question(child)
    child["streak"] += 1
    text = say(f'The child said: "{message}". Beepy is about to ask an English question.',
               "React kindly to what the child said, in ONE short sentence.", "Let's learn something fun! 🌈")
    return text + "\n\n" + child["question"]["q"]


def right_answer(child, question, message):
    child["reason"] = "the child answered correctly"
    child["done"].append(question["q"])
    if record(child, True):
        child["streak"] = 0
        text = say(f'The child answered "{message}" correctly and just reached Level {child["level"]} of 3!',
                   "Celebrate the new level in ONE short sentence.", f"🎉 Hooray! You reached Level {child['level']}!")
    elif child["streak"] >= 4:  # 4 questions in a row: time for a little chat break
        child["question"] = None
        switch(child, "conversation", "a short chat break after 4 questions")
        return say(f'The child answered "{message}" correctly, after 4 questions in a row.',
                   "Cheer, then ask ONE fun question about them: their favorite animal, color or food. "
                   "Use 2 short sentences.",
                   "Yay! You are working so hard! 🌟 What is your favorite animal?", allow_question=True)
    else:
        text = say(f'Beepy asked: "{question["q"]}". The child answered: "{message}". That is RIGHT.',
                   "Cheer for the child in ONE short sentence.", "Yay! You got it! 🎉")
    child["streak"] += 1
    return text + "\n\n" + next_question(child)


def wrong_answer(child, question, message):
    child["reason"] = "the child is trying the question"
    if child["tries"] == 0:  # first miss: encourage, give a hint, same question
        child["tries"] = 1
        text = say(f'Beepy asked: "{question["q"]}". The child answered: "{message}". That is not right yet.',
                   "Encourage them to try again in ONE short sentence. Do NOT say the answer.", "Good try! 💪")
        return text + "\n\n💡 Hint: " + question["hint"]
    record(child, False)  # second miss: show the answer kindly, then move on
    text = say(f'The child tried twice but could not answer: "{question["q"]}".',
               "Say kindly, in ONE short sentence, that trying hard makes our brain grow.",
               "Trying hard makes your brain grow! 🧠")
    child["streak"] += 1
    return f"The answer is: {question['show']} ✨\n\n{text}\n\n{next_question(child)}"


def support(child, message):
    """Comfort first: name the feeling, offer a calming idea, then let the child choose."""
    mood = child["mood"] if child["mood"] in CALM else "sad"
    idea, backup = CALM[mood]
    if child["mode_turns"] == 0:
        return say(f'The child said: "{message}". They seem {mood}.',
                   f"Name the feeling kindly and say it is okay to feel this way. {idea} "
                   "Then ask if they want a game or a new word. Use 2 or 3 short sentences.",
                   backup, allow_question=True)
    return say(f'Beepy said: "{last_beepy(child)}". The child answered: "{message}".',
               "Gently check if they feel a little better, then offer a game or a new word. Use 2 short sentences.",
               "Do you feel a little better? 💛 We can play a game or learn a new word!", allow_question=True)


def game(child, message):
    """Engagement: start a quick game, then react to the child's answer."""
    if child["mode_turns"] == 0:
        idea, backup = GAMES[child["games"] % len(GAMES)]
        child["games"] += 1
        return say(f'The child said: "{message}". Time for a quick game.',
                   f"{idea} Use 2 short sentences.", backup, allow_question=True)
    return say(f'Beepy said: "{last_beepy(child)}". The child answered: "{message}".',
               "Cheer them on, and kindly say the answer if they missed it. Then ask if they are ready "
               "for a new word. Use 2 short sentences.",
               "Ha ha, that was fun! 🎉 Ready for a new word?", allow_question=True)


def chat(child, message):
    """Conversation: show real interest in the child's world."""
    return say(f'Beepy said: "{last_beepy(child)}". The child answered: "{message}".',
               "Show you are interested in ONE short sentence, then ask ONE simple question about it. "
               "If it fits, teach one new English word.",
               "Wow, tell me more! 😊", allow_question=True)


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