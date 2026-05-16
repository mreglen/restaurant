from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Класс настроек приложения, загружаемых из переменных окружения или .env-файла.

    Атрибуты:
        DATABASE_URL (str): URL подключения к базе данных.
        SECRET_KEY (str): Секретный ключ для подписи JWT-токенов.
        ALGORITHM (str): Алгоритм шифрования JWT (например, HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Время жизни access-токена в минутах.
    """

    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        """
        Конфигурация Pydantic для загрузки настроек из файла .env.
        """
        env_file = ".env"


settings = Settings()
"""Экземпляр класса Settings, содержащий загруженные настройки приложения."""