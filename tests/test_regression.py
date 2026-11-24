"""Регрессионные тесты.

Каждый тест соответствует ранее найденному дефекту: он должен проходить
после исправления и падать, если дефект вернётся. Тесты D1 и D2 воспроизводят
ошибки, найденные при тестировании в ЛР №4; остальные закрепляют исправления
ЛР №2–ЛР №3.
"""
import re

import numpy as np
import pytest

from src import client
from src.matrix_sort import format_matrix, input_matrix, sort_desc
from src.service import app, validate_matrix


# --- D1: вывод большой матрицы обрезался многоточием (найдено в ЛР №4) ---

def test_large_matrix_output_is_not_truncated():
    matrix = np.arange(40 * 30, dtype=float).reshape(40, 30)
    text = format_matrix(matrix)
    assert "..." not in text
    assert len(re.findall(r"-?\d+\.\d{3}", text)) == 40 * 30


def test_long_flat_output_is_not_truncated():
    flat = np.linspace(1000.0, 0.0, 1001)
    text = format_matrix(flat)
    assert "..." not in text
    assert len(re.findall(r"-?\d+\.\d{3}", text)) == 1001


# --- D2: клиент падал с AttributeError/KeyError на неверном ответе (ЛР №4) ---

class FakeResponse:
    def __init__(self, body, status_code=200):
        self.status_code = status_code
        self._body = body

    def json(self):
        return self._body


def test_client_rejects_non_object_json(monkeypatch):
    monkeypatch.setattr(client.requests, "post",
                        lambda *args, **kwargs: FakeResponse([1, 2, 3]))
    with pytest.raises(client.IntegrationError):
        client.sort_remote([[1]], retries=0)


def test_client_rejects_response_without_fields(monkeypatch):
    monkeypatch.setattr(client.requests, "post",
                        lambda *args, **kwargs: FakeResponse({"status": "ok"}))
    with pytest.raises(client.IntegrationError):
        client.sort_remote([[1]], retries=0)


# --- Ранее исправленные дефекты (ЛР №2 — ЛР №3) ---

def test_regression_nan_and_inf_rejected_by_service():
    for value in (float("nan"), float("inf"), float("-inf")):
        matrix, problem = validate_matrix({"matrix": [[value]]})
        assert matrix is None
        assert problem[0] == "INVALID_VALUE"


def test_regression_ragged_rows_rejected():
    matrix, problem = validate_matrix({"matrix": [[1, 2], [3]]})
    assert matrix is None
    assert problem[0] == "INVALID_MATRIX"


def test_regression_bool_is_not_number():
    matrix, problem = validate_matrix({"matrix": [[True]]})
    assert matrix is None
    assert problem[0] == "INVALID_VALUE"


def test_regression_version_conflict():
    api = app.test_client()
    resp = api.post("/api/sort", json={"matrix": [[1]]},
                    headers={"X-API-Version": "2.0"})
    assert resp.status_code == 409


def test_regression_input_matrix_skips_nan_and_inf(monkeypatch):
    answers = iter(["nan 1", "inf 2", "3 4"])
    monkeypatch.setattr("builtins.input", lambda *args: next(answers))
    assert input_matrix(1, 2).tolist() == [[3, 4]]


def test_regression_sort_desc_core_behavior():
    flat, result = sort_desc(np.array([[1.0, 2, 3], [4, 5, 6]]))
    assert flat.tolist() == [6, 5, 4, 3, 2, 1]
    assert result.tolist() == [[6, 5, 4], [3, 2, 1]]
