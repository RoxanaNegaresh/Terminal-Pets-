import random
import subprocess
import time
import tkinter as tk

from animation.ascii_art import get_frame


CHECK_INTERVAL_MS = 1500
RENDER_INTERVAL_MS = 80
WINDOW_MARGIN_PX = 20
FONT_FAMILY = "Consolas"
FONT_SIZE = 14
CONTAINER_NAME = "terminal-pet"


class PetOverlay:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Terminal Pet")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#111111")

        self.label = tk.Label(
            self.root,
            text="",
            justify="left",
            bg="#111111",
            fg="#D7FFD7",
            font=(FONT_FAMILY, FONT_SIZE),
            padx=10,
            pady=8,
        )
        self.label.pack()

        self.visible = False
        self.container_running = False
        self.next_container_check = 0.0
        self.next_blink = time.monotonic() + random.uniform(1.0, 2.2)
        self.blink_until = 0.0
        self.prev_frame = ""

        self.root.withdraw()
        self.root.bind("<Escape>", self._close)
        self._tick()

    def _close(self, _event=None) -> None:
        self.root.destroy()

    def _is_container_running(self) -> bool:
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", CONTAINER_NAME],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
        except Exception:
            return False
        return result.returncode == 0 and result.stdout.strip().lower() == "true"

    def _show(self) -> None:
        if self.visible:
            return
        self.root.deiconify()
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = max(0, screen_w - width - WINDOW_MARGIN_PX)
        y = max(0, screen_h - height - WINDOW_MARGIN_PX)
        self.root.geometry(f"+{x}+{y}")
        self.visible = True

    def _hide(self) -> None:
        if not self.visible:
            return
        self.root.withdraw()
        self.visible = False

    def _tick(self) -> None:
        now = time.monotonic()

        if now >= self.next_container_check:
            self.container_running = self._is_container_running()
            self.next_container_check = now + (CHECK_INTERVAL_MS / 1000)
            if self.container_running:
                self._show()
            else:
                self._hide()

        if self.container_running:
            if now >= self.next_blink:
                self.blink_until = now + 0.14
                self.next_blink = now + random.uniform(1.0, 2.2)

            blinking = now < self.blink_until
            frame = get_frame("playful", blink=blinking).strip("\n")
            if frame != self.prev_frame:
                self.label.config(text=frame)
                self.prev_frame = frame
                # Re-anchor after content changes.
                self._show()

        self.root.after(RENDER_INTERVAL_MS, self._tick)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    PetOverlay().run()
