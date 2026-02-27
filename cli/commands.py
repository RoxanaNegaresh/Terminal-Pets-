from typing import Callable

from pet.actions import apply_action
from pet.pet import Pet


def handle_command(pet: Pet, command: str) -> bool:
    return apply_action(pet, command)


def run_interactive_mode(pet: Pet, frame_getter: Callable[[str, bool], str]) -> None:
    while True:
        print(frame_getter(pet.mood, False))
        command = input("Enter command (feed/play/status/exit): ").strip().lower()
        if not handle_command(pet, command):
            break