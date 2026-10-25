import sys
from pydantic_settings import BaseSettings
from pydantic import model_validator
from pathlib import Path

_WEAK_KEY = "pizzaria-secret-key-change-in-production-2024"


class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/pizzaria_checklist"
    SECRET_KEY: str = _WEAK_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = "./uploads"
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:8082",
        "http://localhost:8001",
        "http://localhost",
        "http://127.0.0.1:8082",
    ]
    APP_NAME: str = "Pizzaria Checklist"

    # Usuários semente — lidos do .env, nunca hardcoded no código
    SEED_ADMIN_EMAIL: str = "admin@pizzaria.com"
    SEED_ADMIN_PASSWORD: str = "admin123"
    SEED_MANAGER_EMAIL: str = "gerente@pizzaria.com"
    SEED_MANAGER_PASSWORD: str = "gerente123"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def upload_path(self) -> Path:
        p = Path(self.UPLOAD_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @model_validator(mode="after")
    def production_secrets(self):
        if self.ENV == "production":
            if len(self.SECRET_KEY) < 32 or self.SECRET_KEY.startswith("pizzaria-secret-key"):
                raise ValueError("Defina uma SECRET_KEY aleatória de pelo menos 32 caracteres")
            for password in (self.SEED_ADMIN_PASSWORD, self.SEED_MANAGER_PASSWORD):
                if len(password) < 12 or password in ("admin123", "gerente123"):
                    raise ValueError("Configure senhas iniciais privadas de pelo menos 12 caracteres")
        return self


settings = Settings()
