BASE_URL = "https://needle.aircompany.ai/pls/interno"

PAGE_URL = BASE_URL + "/whsapropriacaoatividades.html"
PROJECTS_ENDPOINT = BASE_URL + "/whsApropriacaoAtividades.get_projects"
REGISTERED_ENDPOINT = BASE_URL + "/whsApropriacaoAtividades.get_registered_appropriations"
APPROPRIATIONS_ENDPOINT = BASE_URL + "/whsApropriacaoAtividades.get_appropriations"
TASKS_ENDPOINT = BASE_URL + "/whsApropriacaoAtividades.get_tasks"
CREATE_ENDPOINT = BASE_URL + "/whsApropriacaoAtividades.create_appropriations"

HEADERS = {
    "Accept": "application/json",
    "Referer": PAGE_URL,
}

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BRIGHT_BLACK = "\033[90m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_GREEN = "\033[92m"