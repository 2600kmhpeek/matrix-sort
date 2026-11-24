"""Модульные тесты клиента REST-сервиса (client.py).

HTTP-обмен имитируется подменой requests.post, поэтому тесты не требуют
запущенного сервиса. Проверяются классы эквивалентности ответов (200, 400,
409, 5xx, не JSON) и граничные случаи повторных попыток.
"""
import numpy as np
import pytest
import requests

from src import client


class FakeResponse:
    """Минимальная имитация requests.Response."""

    def __init__(self, status_code=200, body=None, json_error=False):
        self.status_code = status_code
        self._body = body
        self._json_error = json_error

    def json(self):
        if self._json_error:
            raise ValueError("ответ не является JSON")
        return self._body


def ok_body(flat=None, matrix=None):
    return {
        "status": "ok",
        "sorted_flat": [6.0, 5.0, 4.0, 3.0, 2.0, 1.0] if flat is None else flat,
        "sorted_matrix": [[6.0, 5.0, 4.0], [3.0, 2.0, 1.0]] if matrix is None else matrix,
    }


def test_success_returns_numpy(monkeypatch):
    monkeypatch.setattr(client.requests, "post", lambda *a, **k: FakeResponse(body=ok_body()))
    flat, matrix = client.sort_remote([[1, 2, 3], [4, 5, 6]])
    assert isinstance(flat, np.ndarray)
    assert isinstance(matrix, np.ndarray)
    assert flat.tolist() == [6, 5, 4, 3, 2, 1]
    assert matrix.tolist() == [[6, 5, 4], [3, 2, 1]]


def test_request_payload_and_headers(monkeypatch):
    captured = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        captured.update(url=url, json=json, headers=headers, timeout=timeout)
        return FakeResponse(body=ok_body())

    monkeypatch.setattr(client.requests, "post", fake_post)
    client.sort_remote([[1.5, 2]], url="http://host:9", timeout=1.5)
    assert captured["url"] == "http://host:9/api/sort"
    assert captured["json"] == {"matrix": [[1.5, 2.0]]}
    assert captured["headers"] == {"X-API-Version": client.API_VERSION}
    assert captured["timeout"] == 1.5


def test_http_400_raises_invalid_data(monkeypatch):
    body = {"status": "error", "code": "INVALID_MATRIX", "message": "плохо"}
    monkeypatch.setattr(client.requests, "post", lambda *a, **k: FakeResponse(400, body))
    with pytest.raises(client.InvalidDataError, match="плохо"):
        client.sort_remote([[1]], retries=0)


def test_http_409_raises_version_conflict(monkeypatch):
    body = {"status": "error", "code": "VERSION_CONFLICT", "message": "версия"}
    monkeypatch.setattr(client.requests, "post", lambda *a, **k: FakeResponse(409, body))
    with pytest.raises(client.VersionConflictError, match="версия"):
        client.sort_remote([[1]], retries=0)


def test_http_500_raises_integration_error(monkeypatch):
    monkeypatch.setattr(client.requests, "post", lambda *a, **k: FakeResponse(500, {}))
    with pytest.raises(client.IntegrationError):
        client.sort_remote([[1]], retries=0)


def test_non_json_response_raises_integration_error(monkeypatch):
    monkeypatch.setattr(client.requests, "post",
                        lambda *a, **k: FakeResponse(body=None, json_error=True))
    with pytest.raises(client.IntegrationError, match="не JSON"):
        client.sort_remote([[1]], retries=0)


def test_status_error_in_http_200(monkeypatch):
    body = {"status": "error", "message": "внутренняя ошибка"}
    monkeypatch.setattr(client.requests, "post", lambda *a, **k: FakeResponse(200, body))
    with pytest.raises(client.IntegrationError):
        client.sort_remote([[1]], retries=0)


def test_timeout_retries_then_raises(monkeypatch):
    calls = []

    def fake_post(*args, **kwargs):
        calls.append(1)
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(client.requests, "post", fake_post)
    with pytest.raises(client.ServiceTimeoutError):
        client.sort_remote([[1]], retries=2)
    assert len(calls) == 3


def test_connection_error_retries_then_raises(monkeypatch):
    calls = []

    def fake_post(*args, **kwargs):
        calls.append(1)
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr(client.requests, "post", fake_post)
    with pytest.raises(client.ServiceUnavailableError):
        client.sort_remote([[1]], retries=1)
    assert len(calls) == 2


def test_retry_then_success(monkeypatch):
    calls = []

    def fake_post(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise requests.exceptions.ConnectionError()
        return FakeResponse(body=ok_body())

    monkeypatch.setattr(client.requests, "post", fake_post)
    flat, _ = client.sort_remote([[1, 2, 3], [4, 5, 6]], retries=2)
    assert flat.tolist() == [6, 5, 4, 3, 2, 1]
    assert len(calls) == 2


def test_no_retries_single_attempt(monkeypatch):
    calls = []

    def fake_post(*args, **kwargs):
        calls.append(1)
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(client.requests, "post", fake_post)
    with pytest.raises(client.ServiceTimeoutError):
        client.sort_remote([[1]], retries=0)
    assert len(calls) == 1
