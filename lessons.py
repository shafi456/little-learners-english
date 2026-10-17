"""lessons.py: what Beepy teaches. Three levels that get harder step by step."""

import random
import re
from difflib import get_close_matches

LESSONS = {
    1: [  # Level 1: single words
        {"q": "What animal is this? 🐶", "answers": ["dog", "puppy"], "show": "dog",
         "wrong": ["cat", "fish"], "hint": "It says woof woof! 🐾"},
        {"q": "What color is this apple? 🍎", "answers": ["red"], "show": "red",
         "wrong": ["blue", "green"], "hint": "It's the color of a fire truck! 🚒"},
        {"q": "How many stars? ⭐⭐", "answers": ["two"], "show": "two",
         "wrong": ["one", "three"], "hint": "Count with me: one, ... ✌️"},
        {"q": "What animal is this? 🐱", "answers": ["cat", "kitty", "kitten"], "show": "cat",
         "wrong": ["dog", "cow"], "hint": "It says meow! 🐾"},
        {"q": "What color is this banana? 🍌", "answers": ["yellow"], "show": "yellow",
         "wrong": ["red", "blue"], "hint": "It's the color of the sun! ☀️"},
    ],
    2: [  # Level 2: short phrases
        {"q": "Say the color AND the thing! 🔴⚽", "answers": ["red ball"], "show": "a red ball",
         "wrong": ["a blue ball", "a red car"], "hint": "The color is red, and the thing is a... ⚽"},
        {"q": "How does this face feel? 😊", "answers": ["happy"], "show": "happy",
         "wrong": ["sad", "angry"], "hint": "This face is smiling! 😁"},
        {"q": "How many, and what animal? 🐱🐱", "answers": ["two cat"], "show": "two cats",
         "wrong": ["two dogs", "one cat"], "hint": "Count them... and they say meow!"},
        {"q": "How does this face feel? 😢", "answers": ["sad"], "show": "sad",
         "wrong": ["happy", "sleepy"], "hint": "This face has a tear... 💧"},
        {"q": "We say this when we wake up! ☀️ Good ___?", "answers": ["morning"],
         "show": "Good morning", "wrong": ["Good night", "Thank you"], "hint": "It starts with M... 🌅"},
    ],
    3: [  # Level 3: simple sentences
        {"q": "Where is the cat? 🐱📦 Say: The cat is ...", "answers": ["cat is in box"],
         "show": "The cat is in the box.", "wrong": ["The cat is on the sun.", "The box is a dog."],
         "hint": "The cat is IN the... 📦"},
        {"q": "What color is the sky? Say a whole sentence! 🌤️", "answers": ["sky is blue"],
         "show": "The sky is blue.", "wrong": ["The sky is red.", "The tree is blue."],
         "hint": "Start with: The sky is... 💙"},
        {"q": "What can a bird do? 🐦 Say a whole sentence!", "answers": ["bird can fly"],
         "show": "A bird can fly.", "wrong": ["A bird can swim.", "A fish can fly."],
         "hint": "A bird can... ☁️"},
        {"q": "What food do you like? 🍚🥭 Say: I like ...", "answers": ["i like"],
         "show": "I like mangoes.", "wrong": ["It is a dog.", "I am sleepy."],
         "hint": "Start with: I like... 😋"},
        {"q": "Your friend is sad 😢. What can you say?", "answers": ["are you ok", "are you okay", "i am here"],
         "show": "Are you okay? I am here.", "wrong": ["It is Monday.", "I am a fish."],
         "hint": "You can ask: Are you okay? 💛"},
    ],
}

NUMBERS = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five"}


def clean(text):
    """'I'm 2!!' -> 'i am two'"""
    text = text.lower().replace("i'm", "i am").replace("it's", "it is")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(NUMBERS.get(word, word) for word in text.split())


def base(word):
    """'cats' -> 'cat', so plurals still count."""
    return word[:-1] if len(word) > 3 and word.endswith("s") else word


def has_word(word, words):
    """True if `word` is among `words`, allowing a small typo: 'doge' counts as 'dog'."""
    return bool(get_close_matches(base(word), words, n=1, cutoff=0.8))


def check_answer(question, text):
    """True if the child's answer contains every word of one of the accepted answers."""
    words = [base(w) for w in clean(text).split()]
    for answer in question["answers"]:
        if all(has_word(w, words) for w in answer.split()):
            return True
    return False


def pick_question(level, done, last=None):
    """Prefer questions the child hasn't got right yet, and never repeat the last one."""
    fresh = [q for q in LESSONS[level] if last is None or q["q"] != last["q"]]
    new = [q for q in fresh if q["q"] not in done]
    return random.choice(new or fresh)