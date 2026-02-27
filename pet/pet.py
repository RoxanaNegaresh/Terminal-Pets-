from pet.mood import HAPPY, PLAYFUL


class Pet:
    def __init__(self):
        self.mood = PLAYFUL
        self.xp = 0
        self.hunger = 50

    def feed(self):
        self.hunger -= 10
        self.xp += 5
        self.mood = HAPPY

    def play(self):
        self.xp += 10
        self.mood = PLAYFUL