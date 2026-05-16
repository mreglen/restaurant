from argon2 import PasswordHasher
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY 
"""Секретный ключ, используемый для подписи JWT-токенов."""

ALGORITHM = settings.ALGORITHM 
"""Алгоритм шифрования, используемый для JWT (например, HS256)."""

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES 
"""Время жизни access-токена в минутах."""

ph = PasswordHasher()
"""Экземпляр PasswordHasher для хеширования и верификации паролей с использованием Argon2."""


def hash_password(password: str) -> str:
    """
    Хеширует переданный пароль с использованием алгоритма Argon2.

    Аргументы:
        password (str): Исходный пароль в виде строки.

    Возвращает:
        str: Хеш пароля.
    """
    return ph.hash(password)


def verify_password(password: str, hash_value: str) -> bool:
    """
    Проверяет, соответствует ли переданный пароль заданному хешу.

    Аргументы:
        password (str): Исходный пароль.
        hash_value (str): Хеш, с которым сравнивается пароль.

    Возвращает:
        bool: True, если пароль корректен; иначе False.
    """
    try:
        ph.verify(hash_value, password)
        return True
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Создаёт JWT access-токен с указанными данными и временем жизни.

    Аргументы:
        data (dict): Полезная нагрузка (payload) токена.
        expires_delta (timedelta | None): Опциональный срок действия токена.
                                         Если не указан — используется значение по умолчанию.

    Возвращает:
        str: Подписанный JWT-токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    """
    Декодирует JWT-токен и возвращает его payload.

    Аргументы:
        token (str): JWT-токен для декодирования.

    Возвращает:
        dict | None: Полезная нагрузка токена, если он валиден;
                     None — если токен недействителен или просрочен.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None