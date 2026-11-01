"""Клиент REST-сервиса сортировки: обработка недоступности, таймаутов, ошибок данных."""
import numpy as np
import requests

from src.service import API_VERSION

DEFAULT_URL = "http://127.0.0.1:5000"


class IntegrationError(Exception):
    """Базовое исключение интеграции."""


class ServiceUnavailableError(IntegrationError):
    """Сервис обработки недоступен."""


class ServiceTimeoutError(IntegrationError):
    """Сервис не ответил за отведённое время."""


class InvalidDataError(IntegrationError):
    """Сервис отклонил данные (HTTP 400)."""


class VersionConflictError(IntegrationError):
    """Несовместимые версии API (HTTP 409)."""


def sort_remote(matrix, url=DEFAULT_URL, timeout=3.0, retries=2):
    """Отправляет матрицу в сервис и возвращает (flat, matrix) как массивы NumPy."""
    payload = {"matrix": np.asarray(matrix, dtype=float).tolist()}
    headers = {"X-API-Version": API_VERSION}
    last_error = None
    for _ in range(retries + 1):
        try:
            resp = requests.post(f"{url}/api/sort", json=payload,
                                 headers=headers, timeout=timeout)
        except requests.exceptions.Timeout as exc:
            last_error = ServiceTimeoutError("Превышено время ожидания ответа сервиса")
            last_error.__cause__ = exc
            continue
        except requests.exceptions.ConnectionError as exc:
            last_error = ServiceUnavailableError("Сервис обработки недоступен")
            last_error.__cause__ = exc
            continue
        break
    else:
        raise last_error
    return _parse_response(resp)


def _parse_response(resp):
    try:
        body = resp.json()
    except ValueError:
        raise IntegrationError("Сервис вернул не JSON") from None
    if resp.status_code == 400:
        raise InvalidDataError(body.get("message", "Некорректные данные"))
    if resp.status_code == 409:
        raise VersionConflictError(body.get("message", "Конфликт версий"))
    if resp.status_code != 200 or body.get("status") != "ok":
        raise IntegrationError(f"Неожиданный ответ сервиса: HTTP {resp.status_code}")
    return np.array(body["sorted_flat"]), np.array(body["sorted_matrix"])
