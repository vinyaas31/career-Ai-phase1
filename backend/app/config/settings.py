"""
Central application settings.

Every configurable value in CareerAI is read from environment variables
through this single module. No other file should call os.getenv() directly.

This is what lets us later swap OpenAI <-> local LLM, or dev <-> prod
storage, by changing .env only -- never by editing code.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "CareerAI"
    ENV: str = "development"          # development | production
    DEBUG: bool = True

    # --- CORS (frontend origin allowed to call this API) ---
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # --- Database (wired up in Phase 3, present now so .env is stable) ---
    DATABASE_URL: str = "postgresql://careerai:careerai@localhost:5432/careerai"

    # --- Auth (wired up in Phase 5) ---
    JWT_SECRET: str = "change-me-in-env-file"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # --- AI provider selection (wired up when we reach the AI phases) ---
    LLM_PROVIDER: str = "local"       # "openai" | "local"
    OPENAI_API_KEY: str = ""
    LOCAL_LLM_URL: str = "http://localhost:11434"  # e.g. Ollama

    # --- File storage ---
    STORAGE_PATH: str = "./uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Import this single instance everywhere: `from app.config.settings import settings`
settings = Settings()
