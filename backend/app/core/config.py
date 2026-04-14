from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    APP_NAME: str = "CarRentalMarketplace API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias

    # SurrealDB
    SURREAL_URL: str = "ws://localhost:8000/rpc"
    SURREAL_USER: str = "root"
    SURREAL_PASS: str = "root"
    SURREAL_NAMESPACE: str = "carrental"
    SURREAL_DATABASE: str = "main"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


settings = Settings()
