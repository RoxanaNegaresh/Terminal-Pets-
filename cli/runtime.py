import atexit
import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import time

from animation.ascii_art import get_frame
from pet.pet import Pet
from utils.timers import BlinkTimer

PID_FILE = os.path.join(tempfile.gettempdir(), "terminal_pet_hud.pid")
STOP_FILE = os.path.join(tempfile.gettempdir(), "terminal_pet_hud.stop")


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def render_frame_in_place(frame: str, first_draw: bool) -> bool:
    lines = frame.strip("\n").splitlines()
    line_count = len(lines)

    if not first_draw:
        sys.stdout.write(f"\033[{line_count}F")

    for line in lines:
        sys.stdout.write("\r\033[2K" + line + "\n")

    sys.stdout.flush()
    return False


def move_console_to_corner(width_px: int = 320, height_px: int = 200, margin_px: int = 24) -> None:
    if os.name != "nt":
        return

    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if not hwnd:
        return

    user32 = ctypes.windll.user32
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    x = max(0, screen_w - width_px - margin_px)
    y = max(0, screen_h - height_px - margin_px)
    user32.MoveWindow(hwnd, x, y, width_px, height_px, True)


def spawn_corner_pet_window(entry_script: str) -> bool:
    if os.name != "nt":
        return False

    args = [sys.executable, entry_script, "--live", "--corner-child"]
    try:
        subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
        return True
    except Exception:
        pass

    try:
        quoted = subprocess.list2cmdline([sys.executable, entry_script, "--live", "--corner-child"])
        subprocess.Popen(["cmd", "/c", "start", "", quoted], shell=False)
        return True
    except Exception:
        return False


def spawn_terminal_companion(entry_script: str) -> bool:
    if os.name == "nt":
        return spawn_corner_pet_window(entry_script)

    terminal_commands = [
        ["x-terminal-emulator", "-e", sys.executable, entry_script, "--live"],
        ["gnome-terminal", "--", sys.executable, entry_script, "--live"],
        ["konsole", "-e", sys.executable, entry_script, "--live"],
        ["xterm", "-e", sys.executable, entry_script, "--live"],
    ]

    for args in terminal_commands:
        if shutil.which(args[0]) is None:
            continue
        try:
            subprocess.Popen(args)
            return True
        except Exception:
            continue

    return False


def _read_pid(path: str) -> int | None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            value = handle.read().strip()
        return int(value)
    except Exception:
        return None


def _pid_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def spawn_in_terminal_hud(entry_script: str) -> bool:
    existing_pid = _read_pid(PID_FILE)
    if existing_pid is not None and _pid_is_running(existing_pid):
        return True

    for path in (PID_FILE, STOP_FILE):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except Exception:
            pass

    args = [sys.executable, entry_script, "--hud-child"]

    try:
        subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=None,
            stderr=subprocess.DEVNULL,
            close_fds=False,
        )
        return True
    except Exception:
        return False


def stop_in_terminal_hud() -> bool:
    pid = _read_pid(PID_FILE)
    if pid is None:
        return False

    try:
        with open(STOP_FILE, "w", encoding="utf-8") as handle:
            handle.write("stop\n")
    except Exception:
        pass

    for _ in range(40):
        if not _pid_is_running(pid):
            break
        time.sleep(0.05)

    if _pid_is_running(pid):
        try:
            os.kill(pid, 9)
        except Exception:
            return False

    for path in (PID_FILE, STOP_FILE):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except Exception:
            pass
    return True


def _clear_hud_block(lines: list[str], col: int, row: int) -> None:
    for offset, line in enumerate(lines):
        sys.stdout.write(f"\033[{row + offset};{col}H")
        sys.stdout.write(" " * max(1, len(line)))


def run_in_terminal_hud(pet: Pet) -> None:
    with open(PID_FILE, "w", encoding="utf-8") as handle:
        handle.write(str(os.getpid()))

    def cleanup() -> None:
        try:
            os.remove(PID_FILE)
        except Exception:
            pass
        try:
            os.remove(STOP_FILE)
        except Exception:
            pass

    atexit.register(cleanup)
    prev_lines: list[str] = []
    prev_pos = (1, 1)
    blink_timer = BlinkTimer(min_interval=1.2, max_interval=3.0, duration=0.14)

    while True:
        if os.path.exists(STOP_FILE):
            break

        blinking = blink_timer.is_blinking()
        frame_lines = get_frame(pet.mood, blink=blinking).strip("\n").splitlines()
        width = max(len(line) for line in frame_lines) if frame_lines else 1

        term_size = shutil.get_terminal_size(fallback=(80, 24))
        col = max(1, term_size.columns - width)
        row = 1

        # Always redraw so external clear operations (for example Ctrl+L)
        # repopulate the HUD immediately.
        sys.stdout.write("\033[s")
        if prev_lines:
            _clear_hud_block(prev_lines, prev_pos[0], prev_pos[1])
        for index, line in enumerate(frame_lines):
            padded = line.ljust(width)
            sys.stdout.write(f"\033[{row + index};{col}H{padded}")
        sys.stdout.write("\033[u")
        sys.stdout.flush()

        prev_lines = frame_lines
        prev_pos = (col, row)
        time.sleep(0.08)

    sys.stdout.write("\033[s")
    if prev_lines:
        _clear_hud_block(prev_lines, prev_pos[0], prev_pos[1])
    sys.stdout.write("\033[u")
    sys.stdout.flush()


def spawn_overlay_background(entry_script: str) -> bool:
    if os.name == "nt":
        pythonw = shutil.which("pythonw.exe")
        pyw = shutil.which("pyw")
        exe = pythonw or pyw or sys.executable
        args = [exe, entry_script, "--overlay"]
        subprocess.Popen(args, creationflags=subprocess.CREATE_NO_WINDOW)
        return True

    args = [sys.executable, entry_script, "--overlay"]
    subprocess.Popen(
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return True


def run_live_mode_windows(pet: Pet) -> None:
    first_draw = True
    blink_timer = BlinkTimer(min_interval=1.0, max_interval=2.2, duration=0.14)

    while True:
        blink = blink_timer.is_blinking()
        first_draw = render_frame_in_place(get_frame(pet.mood, blink=blink), first_draw)
        time.sleep(0.08)


def run_live_mode_passive(pet: Pet) -> None:
    first_draw = True
    blink_timer = BlinkTimer(min_interval=1.0, max_interval=2.2, duration=0.14)

    while True:
        blink = blink_timer.is_blinking()
        first_draw = render_frame_in_place(get_frame(pet.mood, blink=blink), first_draw)
        time.sleep(0.08)


def run_docker_live_mode(pet: Pet) -> None:
    blink_timer = BlinkTimer(min_interval=1.0, max_interval=2.2, duration=0.14)

    while True:
        print(get_frame(pet.mood, blink=blink_timer.is_blinking()), flush=True)
        time.sleep(0.25)


def run_auto_mode(pet: Pet) -> None:
    blink_timer = BlinkTimer(min_interval=1.5, max_interval=4.0, duration=0.18)

    while True:
        is_blinking = blink_timer.is_blinking()
        clear_screen()
        print(get_frame(pet.mood, blink=is_blinking))
        print(f"XP: {pet.xp} | Hunger: {pet.hunger} | Mood: {pet.mood}")
        time.sleep(0.1)
