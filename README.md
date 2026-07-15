# Needle Timesheet

> Your timesheet is already filled. You just haven't told Needle yet.

Clicking through dropdowns to allocate 8 hours across 3 projects, twice a day, every day. The data's already there. Your punches, your projects, your tasks. Needle Timesheet reads what Needle already knows, asks you *how much time goes where*, and submits.

## Before / after

**Before:** log into Needle → find the timesheet page → for each period, click "add appropriation" → search the project dropdown → search the task dropdown → type start/end times → type "atv" → repeat. Mistime a click and the dropdown resets.

**After:** `needle` → arrow keys to pick a day → type how many hours per project → enter. Done.

## How it works

1. Reads your Firefox cookies to authenticate with Needle (you must be logged in).
2. Fetches your clock-in/out periods for the day. The punches are already there.
3. Asks how many minutes/hours go to each project. Type `r` on one to dump the remainder.
4. Schedules the allocations across your periods. Asks for a task per project (arrow keys again).
5. Preview, confirm, submit.

That's it. No dropdowns, no searching, no "atv" typing 4 times.

## Install

Grab the `.whl` file and:

```bash
pipx install needletimesheet-0.1.0-py3-none-any.whl
```

On Windows, pip works directly:

```bash
pip install needletimesheet-0.1.0-py3-none-any.whl
```

To upgrade later:

```bash
pipx uninstall needletimesheet
pipx install needletimesheet-0.2.0-py3-none-any.whl
```

Or from source:

```bash
git clone https://github.com/kaiusdepaula/NeedleTimeSheet
cd NeedleTimesheet
uv sync
uv run needle
```

Requires Python ≥ 3.12. Reads cookies from **Firefox** or **Chrome**. Log into Needle in one of them first.

## Usage

```bash
needle
```

Arrow keys to pick a day, type allocations, confirm. That's the happy path.

```bash
needle --lazy
```

Skips the task picker. Automatically selects "Atividade Geral" for every project. Falls back to the picker if it can't find one.

```bash
needle --debug
```

Prints the HTTP request payload before submitting. Good for "is this really what I'm about to send?"

### Duration formats

When asked how much time to allocate, any of these work:

| Input | Means |
|-------|-------|
| `1.5` | 1h30m |
| `90` | 1h30m |
| `1:30` | 1h30m |
| `1h30m` | 1h30m |
| `90m` | 1h30m |
| `r` | dump all remaining minutes here |

## License

MIT
