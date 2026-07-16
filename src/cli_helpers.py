import sys
import os

if os.name == "nt":
    import msvcrt

    def _getch() -> str:
        return msvcrt.getwch()

else:
    import tty
    import termios

    def _getch() -> str:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

from datetime import date
from models import Task
from config import RESET, BOLD, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, BRIGHT_BLACK, BRIGHT_BLUE, BRIGHT_GREEN

UP = {"\x1b[A", "\xe0H"}
DOWN = {"\x1b[B", "\xe0P"}
LEFT = {"\x1b[D", "\xe0K"}
RIGHT = {"\x1b[C", "\xe0M"}
ENTER = {"\r", "\n"}
CTRL_C = {"\x03"}
ESC = {"\x1b"}

def _read_key() -> str:
    """Read a single key press, handling multi-byte escape sequences."""
    ch = _getch()

    if ch in ("\x00", "\xe0"):
        return ch + _getch()

    if ch == "\x1b":
        return ch + _getch() + _getch()

    return ch

def _default_index(available_dates: list[date]) -> int:
    today = date.today()
    if today in available_dates:
        return available_dates.index(today)

    past = [d for d in available_dates if d <= today]
    if past:
        return available_dates.index(max(past))

    return 0


def ask_date(available_dates: list[date]) -> date:
    """This function reupdates the terminal to get correct data input"""
    available_dates = sorted(available_dates)
    idx = _default_index(available_dates)
    print(
        f"{BOLD}Date{RESET} "
        f"({CYAN}\u2190/\u2192{RESET} to move between appropriable days, "
        f"{GREEN}Enter{RESET} to confirm."
    )

    while True:
        day = available_dates[idx]
        sys.stdout.write(
            f"\r{' ' * 50}\r"
            f"> {day.isoformat()} ({day.strftime('%A')})"
            f"  [{idx + 1}/{len(available_dates)}]"
        )
        sys.stdout.flush()

        key = _read_key()

        if key in LEFT:
            idx = max(0, idx - 1)

        elif key in RIGHT:
            idx = min(len(available_dates) - 1, idx + 1)

        elif key in ENTER:
            return day

        elif key in CTRL_C:
            raise KeyboardInterrupt


def ask_task_id(available_tasks: list[Task]) -> int:
    """This function reupdates the terminal to get correct task id"""
    if not available_tasks:
        raise RuntimeError("No tasks found! Shit.")
    idx = 0
    print(
        f"{BOLD}Task{RESET} "
        f"({CYAN}\u2190/\u2192{RESET} to move between appropriable tasks, "
        f"{GREEN}Enter{RESET} to confirm)"
    )
    while True:
        task = available_tasks[idx]
        sys.stdout.write(
            f"\r{' ' * 50}\r"
            f"> {task.descricaoTarefa}"
            f"  [{idx + 1}/{len(available_tasks)}]"
        )
        sys.stdout.flush()
        key = _read_key()
        if key in LEFT:
            idx = max(0, idx - 1)
        elif key in RIGHT:
            idx = min(len(available_tasks) - 1, idx + 1)
        elif key in ENTER:
            return task.codTarefa
        elif key in CTRL_C:
            raise KeyboardInterrupt
