from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Добавляем описание
    app_title: str
    description: str
    version: str

    # Добавляем недостающие параметры для Postgres
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Добавляем параметры для Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # Добавляем параметры для почты отправки
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_PASSWORD: str

    # Добавляем параметры для почты считывания
    IMAP_SERVER: str
    IMAP_PORT: int
    EMAIL_ACCOUNT: str
    EMAIL_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
