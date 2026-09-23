from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = 'SLOPESHIELD NER API'
    environment: str = 'development'
    database_url: str = 'sqlite:///./SLOPESHIELD.db'
    cors_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    model_path: str = 'models/landslide_model.joblib'
    nasa_glc_url: str = 'https://data.nasa.gov/docs/legacy/Global_Landslide_Catalog_Export/Global_Landslide_Catalog_Export_rows.csv'
    weather_provider: str = 'open-meteo'
    model_name: str = 'xgboost'
    model_version: str = 'untrained'
    monitoring_enabled: bool = True
    monitoring_interval_minutes: int = 5

    # Telegram notifications
    telegram_bot_token: str = ''
    telegram_chat_id: str = ''

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore'
    )

    @property
    def resolved_model_path(self):
        p = Path(self.model_path)
        if p.is_absolute():
            return p

        # Accept both backend-relative paths (models/...)
        # and project-relative paths (backend/models/...).
        backend_root = Path(__file__).resolve().parents[1]
        project_root = backend_root.parent

        if str(p).replace('\\', '/').startswith('backend/'):
            return project_root / p

        return backend_root / p

    @property
    def cors_list(self):
        return [
            x.strip()
            for x in self.cors_origins.split(',')
            if x.strip()
        ]


@lru_cache
def get_settings():
    return Settings()