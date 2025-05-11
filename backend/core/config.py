from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    GOOGLE_KEY: str
    FOURSQUARE_API_KEY: str
    APIS_ENABLED: bool = True
    CACHE_TTL_HOURS: int = 12
    DEV_MODE: bool = False

    # --- add this ---
    INSTAGRAM_TOKEN: str | None = None


    class Config:
        env_file = ".env"

_settings = None
def get_settings():
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
