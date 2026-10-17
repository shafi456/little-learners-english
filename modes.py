"""modes.py: reads the child's message and picks Beepy's mode.

Simple keyword rules: they run instantly, and every decision can be explained.
    learning      teach the next word, phrase or sentence
    conversation  chat about the child's world
    engagement    a quick game to bring the fun back
    support       the child seems upset: comfort comes first
"""

from lessons import clean

# Checked from top to bottom, so "not happy" counts as sad before "happy" is checked.
MOODS = {
    "sad": ["sad", "not happy", "not good", "cry", "crying", "upset", "lonely", "miss", "😢", "😭", "😞"],
    "angry": ["angry", "mad", "hate", "😠", "😡"],
    "scared": ["scared", "afraid", "nightmare", "😨", "😱"],
    "tired": ["tired", "sleepy", "sleep", "😴", "🥱"],
    "frustrated": ["too hard", "so hard", "difficult", "i can not", "give up"],
    "bored": ["boring", "bored"],
    "happy": ["happy", "good", "great", "fun", "yay", "😊", "😀", "😄"],
}
UPSET = ["sad", "angry", "scared", "tired", "frustrated"]

PLAY = ["play", "game", "story", "song", "riddle", "no"]
CHAT = ["my", "i have", "i went", "i saw", "do you", "are you", "what is your", "who are you",
        "mom", "dad", "ammu", "abbu", "friend", "school"]
READY = ["ok", "okay", "yes", "ready", "learn", "word", "next", "again"]


def has_any(text, phrases):
    """True if any phrase appears as whole words ('no' is not found in 'nose'). Emojis are matched as they are."""
    words = f" {clean(text)} "
    return any((f" {p} " in words) if p.isascii() else (p in text) for p in phrases)


def detect_mood(text):
    """'i am so sad 😢' -> 'sad'. Returns None if no feeling is mentioned."""
    for mood, phrases in MOODS.items():
        if has_any(text, phrases):
            return mood
    return None


def choose_mode(child, text, mood):
    """Pick the mode for this reply. Returns (mode, reason)."""
    if mood in UPSET:
        return "support", f"the child seems {mood}"
    if mood == "bored" or has_any(text, PLAY):
        return "engagement", "the child wants to play"
    long_chat = child["mode"] == "conversation" and child["mode_turns"] >= 3
    if has_any(text, CHAT) and not long_chat:
        return "conversation", "the child is sharing or asking something"
    if has_any(text, READY) or mood == "happy":
        return "learning", "the child is ready to learn"
    if child["mode"] in ("support", "engagement", "conversation") and child["mode_turns"] < 2:
        return child["mode"], "staying a little longer before the lesson"
    return "learning", "back to the lesson"