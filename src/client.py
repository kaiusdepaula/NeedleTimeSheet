import browser_cookie3
import httpx
import json
import re
import os
import sys

from config import PAGE_URL, PROJECTS_ENDPOINT, REGISTERED_ENDPOINT, APPROPRIATIONS_ENDPOINT, \
    TASKS_ENDPOINT, CREATE_ENDPOINT, HEADERS

from pydantic import TypeAdapter
from models import Project, Task, AppropriationsResponse, Appropriation, CreateAppropriation, CreateAppropriationRequest

from datetime import date

if sys.platform == "win32":
    import truststore
    truststore.inject_into_ssl()

def _get_cookies():
    """Load Needle auth cookies from the browser, trying host and domain patterns."""
    for source in [browser_cookie3.firefox, browser_cookie3.chrome, browser_cookie3.edge]:
        try:
            for domain in (
                "needle.aircompany.ai", # Works in Linux
                ".aircompany.ai" # Works in Windows
            ):
                cj = source(domain_name=domain)
                if list(cj):
                    return cj
        except browser_cookie3.BrowserCookieError:
            continue
    raise RuntimeError(
        "No Needle cookies found in Firefox, Chrome, or Edge. "
        "Log into Needle in one of them first."
    )


class NeedleClient:
    def __init__(self):
        self.client = httpx.Client(
            cookies=_get_cookies(),
            headers=HEADERS,
            timeout=30,
        )
    def _get(self, endpoint: str, **params) -> dict:
        response = self.client.get(
            endpoint,
            params={
                "p_params": json.dumps(params)
            },
        )
        response.raise_for_status()
        return response.json()

    def get_projects(self, dataAppropriation: date) -> list[Project]:
        return TypeAdapter(list[Project]).validate_python(
            self._get(
            PROJECTS_ENDPOINT,
            dataAppropriation=dataAppropriation.isoformat(),
            )
        )

    def get_tasks(self, dataAppropriation: date, p_id_projeto: int) -> list[Task]:
        return TypeAdapter(list[Task]).validate_python(
            self._get(
                TASKS_ENDPOINT,
                dataAppropriation=dataAppropriation.isoformat(),
                p_id_projeto=p_id_projeto,
            )
        )


    def get_user_id(self) -> int:
        """Scrape the logged-in user's ID from the Needle page. Cached to ~/.needle_user_id."""
        cache = ".needle_user_id"
        if os.path.exists(cache):
            return int(open(cache).read().strip())

        resp = self.client.get(PAGE_URL)
        resp.raise_for_status()
        m = re.search(r'\{userId:\s*(\d+)\}', resp.text)
        if not m:
            raise RuntimeError("Could not find userId in page HTML.")
        user_id = int(m.group(1))
        open(cache, "w").write(str(user_id))
        return user_id

    def get_appropriations(self, user_id: int) -> list[Appropriation]:
        return TypeAdapter(AppropriationsResponse).validate_python(
            self._get(
                APPROPRIATIONS_ENDPOINT,
                userId=user_id,
            )
        ).items

    def get_registered_appropriations(self, user_id: int) -> list[Appropriation]:
        return TypeAdapter(AppropriationsResponse).validate_python(
            self._get(
                REGISTERED_ENDPOINT,
                userId=user_id,
            )
        ).items

    def submit(self, payload: CreateAppropriationRequest):
        print(TypeAdapter(CreateAppropriationRequest).dump_json(payload))
        response = self.client.post(
            CREATE_ENDPOINT,
            files={
                    "p_data": (
                        None,
                        TypeAdapter(CreateAppropriationRequest).dump_json(payload),
                        "application/json",
                    )
            }, 
        )
        response.raise_for_status()
        return response

if __name__ == "__main__":
    from config import USER_ID
    print(NeedleClient().get_tasks(dataAppropriation=date.fromisoformat("2026-07-08"), p_id_projeto=7844))
    # print(NeedleClient().get_appropriations(user_id=USER_ID))
    # print(NeedleClient().get_registered_appropriations(user_id=USER_ID))
    # print(NeedleClient().get_projects(dataAppropriation=date.fromisoformat("2026-07-08")))
#     NeedleClient().submit(
#         payload=TypeAdapter(CreateAppropriationRequest).validate_json(
#             """
# {
#   "appropriationsFirstPeriod": [
#     {
#       "hourEntry": "08:55",
#       "hourDeparture": "11:55",
#       "hourType": "Normal",
#       "projectId": 6460,
#       "taskId": 62448,
#       "observation": "atv",
#       "date": "2026-07-07",
#       "origem": "PONTO",
#       "segmentoId": null,
#       "seqJornadaReal": 1
#     },
#     {
#       "projectId": 6070,
#       "taskId": 61652,
#       "hourEntry": "11:56",
#       "hourDeparture": "11:57",
#       "observation": "atv",
#       "date": "2026-07-07",
#       "origem": null,
#       "segmentoId": null,
#       "seqJornadaReal": null
#     }
#   ],
#   "appropriationsSecondPeriod": [
#     {
#       "hourEntry": "12:58",
#       "hourDeparture": "13:58",
#       "hourType": "Normal",
#       "projectId": 6460,
#       "taskId": 62448,
#       "observation": "atv",
#       "date": "2026-07-07",
#       "origem": "PONTO",
#       "segmentoId": null,
#       "seqJornadaReal": 2
#     },
#     {
#       "projectId": 7844,
#       "taskId": 67099,
#       "hourEntry": "13:59",
#       "hourDeparture": "14:59",
#       "observation": "atv",
#       "date": "2026-07-07",
#       "origem": null,
#       "segmentoId": null,
#       "seqJornadaReal": null
#     },
#     {
#       "projectId": 6070,
#       "taskId": 61652,
#       "hourEntry": "15:00",
#       "hourDeparture": "17:55",
#       "observation": "atv",
#       "date": "2026-07-07",
#       "origem": null,
#       "segmentoId": null,
#       "seqJornadaReal": null
#     }
#   ],
#   "appropriationsThirdPeriod": [],
#   "appropriationsFourthPeriod": []
# }
# """
#         )
#     )
