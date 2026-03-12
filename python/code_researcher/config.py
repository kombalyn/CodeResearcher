import os
from enum import Enum
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Mode(Enum):
    FREE = "free"
    PAID = "paid"

class ResearcherConfig:
    def __init__(self, github_token=None, mode=None, max_results=None,
                 max_chars_per_file=None, timeout=None,
                 use_github=None, use_grep_app=None, use_stackoverflow=None):
        load_dotenv()
        self.github_token = (github_token or os.getenv("GITHUB_TOKEN", "")).strip()
        self.max_chars_per_file = max_chars_per_file or int(os.getenv("RESEARCHER_MAX_CHARS", "1500"))
        self.timeout = timeout or int(os.getenv("RESEARCHER_TIMEOUT", "10"))
        self.use_github = use_github if use_github is not None else os.getenv("RESEARCHER_USE_GITHUB", "true").lower() == "true"
        self.use_grep_app = use_grep_app if use_grep_app is not None else os.getenv("RESEARCHER_USE_GREP_APP", "true").lower() == "true"
        self.use_stackoverflow = use_stackoverflow if use_stackoverflow is not None else os.getenv("RESEARCHER_USE_SO", "false").lower() == "true"
        if mode is not None:
            self.mode = mode
        else:
            env_mode = os.getenv("RESEARCHER_MODE", "").lower()
            if env_mode == "paid":
                self.mode = Mode.PAID
            elif env_mode == "free":
                self.mode = Mode.FREE
            else:
                self.mode = Mode.PAID if self.github_token else Mode.FREE
        if max_results is not None:
            self.max_results = max_results
        else:
            env_max = os.getenv("RESEARCHER_MAX_RESULTS", "")
            self.max_results = int(env_max) if env_max.isdigit() else (10 if self.mode == Mode.PAID else 3)

    @property
    def is_paid(self):
        return self.mode == Mode.PAID and bool(self.github_token)

    @property
    def auth_headers(self):
        h = {"Accept": "application/vnd.github+json"}
        if self.is_paid:
            h["Authorization"] = f"Bearer {self.github_token}"
        return h
