import os
import sys

from animation.ascii_art import get_frame
from cli.commands import run_interactive_mode
from cli.runtime import (
    move_console_to_corner,
    run_auto_mode,
    run_docker_live_mode,
    run_in_terminal_hud,
    run_live_mode_passive,
    run_live_mode_windows,
    spawn_corner_pet_window,
    spawn_in_terminal_hud,
    spawn_overlay_background,
    spawn_terminal_companion,
    stop_in_terminal_hud,
)
from pet.pet import Pet

sys.stdout.reconfigure(encoding="utf-8")

try:
    import msvcrt
except ImportError:
    msvcrt = None


def run_overlay_mode() -> None:
    from cli.pet_overlay import PetOverlay

    PetOverlay().run()


def main() -> None:
    entry_script = os.path.abspath(__file__)

    if "--hud" in sys.argv:
        if not spawn_in_terminal_hud(entry_script):
            print("Could not start in-terminal pet HUD.")
        return

    if "--hud-stop" in sys.argv:
        if not stop_in_terminal_hud():
            print("No running in-terminal pet HUD found.")
        return

    if "--hud-child" in sys.argv:
        run_in_terminal_hud(Pet())
        return

    if "--companion" in sys.argv:
        if not spawn_terminal_companion(entry_script):
            print("Could not launch a companion terminal window on this system.")
        return

    if "--background" in sys.argv:
        spawn_overlay_background(entry_script)
        return

    if "--overlay" in sys.argv:
        run_overlay_mode()
        return

    if "--corner" in sys.argv and "--corner-child" not in sys.argv:
        spawn_corner_pet_window(entry_script)
        return

    pet = Pet()

    if "--docker-live" in sys.argv:
        run_docker_live_mode(pet)
        return

    if "--passive-live" in sys.argv:
        run_live_mode_passive(pet)
        return

    if "--corner-child" in sys.argv:
        move_console_to_corner()

    if not sys.stdin.isatty():
        run_auto_mode(pet)
        return

    if "--live" in sys.argv and msvcrt is not None:
        run_live_mode_windows(pet)
    else:
        run_interactive_mode(pet, get_frame)


if __name__ == "__main__":
    main()
