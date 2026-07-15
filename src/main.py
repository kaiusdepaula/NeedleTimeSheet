from __future__ import annotations
from datetime import date
import httpx
import argparse 

from config import RESET, BOLD, RED, GREEN, \
    YELLOW, BLUE, MAGENTA, CYAN, BRIGHT_BLACK, BRIGHT_BLUE, BRIGHT_GREEN
from client import NeedleClient
from cli_helpers import ask_date
from utils import get_day_periods, build_payload, print_payload, print_preview
from compute import ask_allocations, total_minutes_in_periods, schedule_allocations


def main():
    try:
        parser = argparse.ArgumentParser(
                    description='Automatically fills project allocation within dynamic period timelines.',
                    usage='%(prog)s [options]'
        )
        parser.add_argument(
            '--debug',
            help='Prints HTTP requests and verbose outputs.',
            action="store_true"
        )
        parser.add_argument(
            '--lazy',
            help='Searches for "Atividade Geral" task automatically and fallsback only if not found.',
            action="store_true"
        )
        arguments =  parser.parse_args()

        print(f"{BRIGHT_BLACK}{'=' * 70}{RESET}")
        print(f"{BOLD}{CYAN}Needle Timesheet{RESET}")
        print(f"{BRIGHT_BLACK}{'=' * 70}{RESET}")
        print(f"\n{YELLOW}Connecting...{RESET}")
        client = NeedleClient()
        user_id = client.get_user_id()

        print("Fetching appropriable days...")
        appropriations_list = client.get_appropriations(user_id)
        available_dates = [
            date.fromisoformat(item.data)
            for item in appropriations_list
        ]
        day = ask_date(available_dates)

        print("\nFetching projects...")
        projects = client.get_projects(day)

        if not projects:
            raise RuntimeError(
                "No projects available."
            )

        print(
            f"Found {len(projects)} projects."
        )

        periods = get_day_periods(appropriations_list, day)
        print(
            f"Found {len(periods)} period(s), "
            f"{total_minutes_in_periods(periods) // 60}h"
            f"{total_minutes_in_periods(periods) % 60:02d}m total."
        )

        allocations = ask_allocations(
            projects,
            total_minutes_in_periods(periods),
        )

        if not allocations:
            print("Nothing to submit.")
            return

        intervals = schedule_allocations(
            periods,
            allocations,
            lazy =  arguments.lazy,
        )
        observation = input("\nObservation (default = atv):").strip()
        observation = "atv" if observation == "" else observation

        print_preview(day, intervals)

        payload = build_payload(day, intervals, observation)
        if arguments.debug:
            print_payload(payload)

        submission_flag = (
            input(f"{BOLD}Submit (default={GREEN}y{RESET})?{RESET} [{GREEN}y{RESET}/{BRIGHT_BLACK}N{RESET}] ")
            .strip()
            .lower()
            in ("y", "yes", "")
        )
        if not submission_flag:
            print(f"{YELLOW}Cancelled.{RESET}")
            return

        print(f"{CYAN}Submitting...{RESET}")
        response = client.submit(payload)

        if arguments.debug:
            print(f"\n{BOLD}HTTP{RESET} {CYAN}{response.status_code}{RESET}")
        print(f"{GREEN}✓ Success{RESET}")

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Cancelled.{RESET}")

    except httpx.HTTPStatusError as exc:
        print(f"{RED}{BOLD}HTTP Error{RESET}")
        print(exc)

        if exc.response.content:
            print(exc.response.text)

    except Exception as exc:
        print(type(exc).__name__)
        print(exc)

if __name__ == "__main__":
    main()