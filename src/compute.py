from datetime import timedelta
from models import Allocation, Project, Period, Allocation, Interval
from utils import parse_duration
from cli_helpers import ask_task_id

from client import NeedleClient

def total_minutes_in_allocations(
    allocations: list[Allocation],
) -> int:
    return sum(
        a.minutes
        for a in allocations
    )

def total_minutes_in_periods(
    periods: list[Period],
) -> int:
    return sum(
        p.minutes
        for p in periods
    )

def ask_allocations(
    projects: list[Project],
    total_minutes: int,
) -> list[Allocation]:
    print("=" * 60)
    print("Hours per project (blank/0 skip, 'r' = rest of the day)")
    print("Either fill in your whole day or elect a day to have all remaining minutes.")
    print("=" * 60)

    explicit: list[Allocation] = []
    rest_project: Project = None
    for project in projects:
        remaining = total_minutes - total_minutes_in_allocations(explicit)
        duration = input(
            f"\n{project.name}\n"
            f"Remaining: {remaining // 60}h{remaining % 60:02d}m\n"
            f"Duration (eg: 1, 1.0, 60m, 1h00m, 01:00, r=rest) [skip]: "
        ).strip()

        if duration.lower() in ("r", "rest"):
            if rest_project is not None:
                print(
                    f"Rest already assigned to "
                    f"{rest_project.name}, ignoring."
                )
                continue
            elif rest_project is None:
                rest_project = project
                continue

        try:
            minutes = parse_duration(duration)
        except ValueError:
            print(f"Invalid duration number detected. Skipping project {project.name}")
            continue
        
        if not duration:
            continue
        
        if minutes > remaining:
            print("\nProject excels maximum amount of minutes available.")
            print(f"Minutes declared: {minutes}")
            print(f"Minutes remaining: {remaining}")
            raise RuntimeError("Try again with different values.")

        explicit.append(
            Allocation(
                project=project,
                minutes=minutes,
            )
        )

    allocations = list(explicit)
    rest_allocation: Allocation = None
    remaining = total_minutes - total_minutes_in_allocations(explicit)

    if remaining > 0 and rest_project is None:
        print(f"\nMissing {remaining} minutes to allocate and no project selected to receive these minutes.")
        raise RuntimeError("You need to select a project to fill the rest of the day.")
    else:
        # IMPORTANT: rest_allocation will ALWAYS be last.
        rest_allocation = Allocation(
            project=rest_project,
            minutes=remaining,
        )
        allocations.append(rest_allocation)
    return allocations


def schedule_allocations(
    periods: list[Period],
    allocations: list[Allocation],
    lazy: bool,
) -> list[Interval]:
    
    client = NeedleClient()
    intervals: list[Interval] = []
    period_index = 0
    periods_touched: set[int] = set()
    gap = timedelta(minutes=1)

    for allocation in allocations:
        remaining = allocation.minutes
        while remaining > 0:
            if period_index >= len(periods):
                print("\nTruncating 'rest' allocation to period's end due to gap overlap.")
                break

            current = periods[period_index]
            # If this period has been touched, we need to add a one minute gap.
            if period_index in periods_touched:
                current.start += gap

            available = int((current.end - current.start).total_seconds() // 60)
            if available <= 0:
                period_index += 1
                continue

            take = min(remaining, available)
            interval_start = current.start
            interval_end = interval_start + timedelta(minutes=take)

            available_tasks = client.get_tasks(
                dataAppropriation=interval_end.date(), 
                p_id_projeto=allocation.project.id
            )
            taskid = None
            if lazy:
                # Silently fails and fallsback into regular function
                try:
                    taskid = [
                        task for task in available_tasks 
                        if task.descricaoTarefa=="Atividade Geral"
                    ][0].codTarefa
                except:
                    taskid = None
            if not taskid:
                print("=" * 60)
                print(f"Please choose a task for:")
                print(f"{allocation.project.name}")
                print("=" * 60)
                taskid = ask_task_id(available_tasks)

            intervals.append(
                Interval(
                    project=allocation.project,
                    start=interval_start,
                    end=interval_end,
                    taskid=taskid,
                    period_index=period_index,
                )
            )
            periods_touched.add(period_index)
            current.start = interval_end
            remaining -= take
            if current.start >= current.end:
                period_index += 1

    return intervals


if __name__ == "__main__":
    from config import USER_ID
    from client import NeedleClient
    from datetime import date
    from utils import get_day_periods
    client = NeedleClient()

    appropriations_list = client.get_appropriations(USER_ID)
    periods = get_day_periods(appropriations_list, date.fromisoformat("2026-07-08"))
    available = total_minutes_in_allocations(periods)

    projects = client.get_projects(dataAppropriation=date.fromisoformat("2026-07-08"))
    allocations = ask_allocations(projects, available)

    intervals = schedule_allocations(
        periods,
        allocations
    )
    print(intervals)