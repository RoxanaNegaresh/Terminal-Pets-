from pet.mood import GRUMPY, HAPPY, PLAYFUL, normalize_mood

ASCII_FRAMES = {
    HAPPY: {
        "open": r"""
 /\_/\
( ^.^ )  Mood: Happy
 > ^ <
""",
        "closed": r"""
 /\_/\
( -.- )  Mood: Happy
 > ^ <
""",
    },
    PLAYFUL: {
        "open": r"""
 /\_/\
( o.o )  Mood: Playful
 > ^ <
""",
        "closed": r"""
 /\_/\
( -.- )  Mood: Playful
 > ^ <
""",
    },
    GRUMPY: {
        "open": r"""
 /\_/\
( -.- )  Mood: Grumpy
 > ^ <
""",
        "closed": r"""
 /\_/\
( -.- )  Mood: Grumpy
 > ^ <
""",
    },
}


def get_frame(mood: str, blink: bool = False) -> str:
    mood_frames = ASCII_FRAMES[normalize_mood(mood)]
    return mood_frames["closed"] if blink else mood_frames["open"]