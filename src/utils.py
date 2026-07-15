import re
import json
from pydantic import TypeAdapter
from datetime import date, datetime
from models import Period, Appropriation, Interval, CreateAppropriationRequest, CreateAppropriation
from config import RESET, BOLD, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, BRIGHT_BLACK, BRIGHT_BLUE, BRIGHT_GREEN

def parse_duration(value: str) -> int:
    """This function is used to parse input from the user when asking for appropriation duration."""
    value = value.strip().lower()

    if value == "":
        return 0

    if re.fullmatch(r"\d+(?:\.\d+)?", value):
        return round(float(value) * 60)

    if re.fullmatch(r"\d+:\d\d", value):
        h, m = value.split(":")
        return int(h) * 60 + int(m)

    m = re.fullmatch(r"(\d+(?:\.\d+)?)h", value)
    if m:
        return round(float(m.group(1)) * 60)

    m = re.fullmatch(r"(\d+)m", value)
    if m:
        return int(m.group(1))

    m = re.fullmatch(r"(\d+)h(\d+)m", value)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    
    raise ValueError(f"Invalid duration: {value}")

def parse_clock(day: date, value: str):
    return datetime.combine(
        day,
        datetime.strptime(value, "%H:%M").time(),
    )

def get_day_periods(
    items: list[Appropriation],
    day: date,
) -> list[Period]:
    """
    Turn the punches for `day`, taken from a get_appropriations
    items list, into Periods.

    Raises RuntimeError if there's no punch record for that day,
    or if it's already been submitted (in which case it won't show
    up here anymore).
    """
    day_entry = next(
        (item for item in items if item.data == day.isoformat()),
        None,
    )

    if day_entry is None:
        raise RuntimeError(
            f"No appropriable punch record found for {day.isoformat()}. "
            "Either you haven't clocked in/out for this day yet, "
            "or it's already been submitted."
        )

    hours = day_entry.hours
    if not hours:
        raise RuntimeError(
            f"Punch record for {day.isoformat()} has no hours entries."
        )

    periods = []
    for hour in sorted(hours, key=lambda h: h.seq):
        periods.append(
            Period(
                start=parse_clock(day, hour.hourEntry),
                end=parse_clock(day, hour.hourDeparture),
            )
        )

    return periods


def print_preview(
    day: date,
    intervals: list[Interval],
) -> None:
    print(f"{BRIGHT_BLACK}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN}{day.isoformat()}{RESET}")
    print(f"{BRIGHT_BLACK}{'=' * 70}{RESET}")

    last_period = None
    total = 0

    for interval in intervals:
        if interval.period_index != last_period:
            if interval.period_index == 0:
                title = "Morning"
            elif interval.period_index == 1:
                title = "Afternoon"
            else:
                title = f"Period {interval.period_index + 1}"

            print(f"\n{BOLD}{YELLOW}{title}{RESET}")
            print(f"{BRIGHT_BLACK}{'-' * 70}{RESET}")
            last_period = interval.period_index

        minutes = int(
            (interval.end - interval.start).total_seconds() // 60
        )
        total += minutes

        print(
            f"{GREEN}{interval.start.strftime('%H:%M')}{RESET}"
            f" {BRIGHT_BLACK}→{RESET} "
            f"{GREEN}{interval.end.strftime('%H:%M')}{RESET}   "
            f"{BOLD}{interval.project.name}{RESET}"
        )

    print(f"{BRIGHT_BLACK}{'-' * 70}{RESET}")
    print(
        f"{BOLD}Total:{RESET} "
        f"{CYAN}{total // 60}h{total % 60:02d}m{RESET}"
    )


def build_payload(
    day: date,
    intervals: list[Interval],
    observation: str,
) -> CreateAppropriationRequest:
    periods = [[] for _ in range(4)]
    first_interval_in_period = {}

    for interval in intervals:
        idx = interval.period_index
        first = idx not in first_interval_in_period
        first_interval_in_period[idx] = True

        appropriation = CreateAppropriation(
            hourEntry=interval.start.strftime("%H:%M"),
            hourDeparture=interval.end.strftime("%H:%M"),
            projectId=interval.project.id,
            taskId=interval.taskid,
            observation=observation,
            date=day,
            hourType="Normal" if first else None,
            origem="PONTO" if first else None,
            seqJornadaReal=idx + 1 if first else None,
        )
        periods[idx].append(appropriation)

    return CreateAppropriationRequest(
        appropriationsFirstPeriod = periods[0],
        appropriationsSecondPeriod = periods[1],
        appropriationsThirdPeriod = periods[2],
        appropriationsFourthPeriod = periods[3],
    )

def print_payload(payload: CreateAppropriationRequest) -> None:
    print("=" * 70)
    print("Payload")
    print("=" * 70)
    print(
        json.dumps(
            TypeAdapter(CreateAppropriationRequest).dump_python(
                payload,
                mode="json",
            ),
            indent=2,
            ensure_ascii=False,
        )
    )
if __name__ == "__main__":
    from config import USER_ID
    from client import NeedleClient
    from models import Project
    # appropriations_list = NeedleClient().get_appropriations(user_id=USER_ID)
    # available_dates = [
    #     date.fromisoformat(item.data)
    #     for item in appropriations_list
    # ]
    day = date(2026, 7, 8)
    intervals = [
        Interval(project=Project(id=7844, name='Compass Inc - Humantic AI - Bedrock Migration Readiness Assess'), start=datetime(2026, 7, 8, 8, 52), end=datetime(2026, 7, 8, 9, 52), taskid=67099, period_index=0), 
        Interval(project=Project(id=6460, name='Compass Inc - Nsight Live - Twilio to Connect Mobilize'), start=datetime(2026, 7, 8, 9, 53), end=datetime(2026, 7, 8, 12, 17), taskid=62448, period_index=0), 
        Interval(project=Project(id=6460, name='Compass Inc - Nsight Live - Twilio to Connect Mobilize'), start=datetime(2026, 7, 8, 13, 18), end=datetime(2026, 7, 8, 14, 54), taskid=62448, period_index=1), 
        Interval(project=Project(id=6070, name='Compass - Mayflower INC - Profissionais part-time (non-billable)'), start=datetime(2026, 7, 8, 14, 55), end=datetime(2026, 7, 8, 18, 1), taskid=61652, period_index=1)]
    observation = "atv"
    payload = build_payload(day, intervals, observation)
    print_payload(payload)