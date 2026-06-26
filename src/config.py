import os
from functools import lru_cache
from pathlib import Path

class Settings:
    def __init__(
        self,
        kill_switch_file: str | None = None,
        kill_switch_enabled: bool | None = None,
        groq_api_key: str | None = None,
        app_env: str | None = None,
        model_name: str | None = None,
    ):
        self.kill_switch_file = kill_switch_file or os.getenv("KILL_SWITCH_FILE", "/tmp/egov_killswitch.flag")
        
        # Check env or default
        if kill_switch_enabled is not None:
            self.kill_switch_enabled = kill_switch_enabled
        else:
            self.kill_switch_enabled = os.getenv("KILL_SWITCH_ENABLED", "false").lower() == "true"
            
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
        self.app_env = app_env or os.getenv("APP_ENV", "development")
        self.model_name = model_name or os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
        self.PROJECT_NAME = "Mini Projet Agents - Multi-Secteurs"

    @property
    def is_killed(self) -> bool:
        if self.kill_switch_enabled:
            return True
        if self.kill_switch_file and Path(self.kill_switch_file).exists():
            return True
        return False

@lru_cache()
def get_settings():
    return Settings()