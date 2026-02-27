PLAYFUL = "playful"
HAPPY = "happy"
GRUMPY = "grumpy"

DEFAULT_MOOD = PLAYFUL
ALL_MOODS = {PLAYFUL, HAPPY, GRUMPY}


def normalize_mood(value: str) -> str:
    value = (value or "").strip().lower()
    return value if value in ALL_MOODS else DEFAULT_MOOD