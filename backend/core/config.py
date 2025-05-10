from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_KEY: str
    FOURSQUARE_API_KEY: str  # ← Add this line
    APIS_ENABLED: bool = True
    CACHE_TTL_HOURS: int = 12
    DEV_MODE: bool = False

    class Config:
        env_file = ".env"

_settings = None
def get_settings():
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
