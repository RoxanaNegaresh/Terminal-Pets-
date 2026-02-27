from pet.pet import Pet


def apply_action(pet: Pet, command: str) -> bool:
    if command == "feed":
        pet.feed()
    elif command == "play":
        pet.play()
    elif command == "status":
        pass
    elif command == "exit":
        return False
    elif command:
        print("Unknown command")
    return True