"""Модульные тесты интегрированного приложения (integrated_app.py).

Проверяется сценарий «ввод -> сервис -> вывод» без реального HTTP:
модуль клиента подменяется, а ввод — функцией-заглушкой.
"""
import numpy as np
import pytest

from src import integrated_app
from src.client import ServiceUnavailableError


@pytest.fixture
def sample():
    return np.array([[1.0, 4.0], [3.0, 2.0]])


def test_run_once_success(monkeypatch, capsys, sample):
    calls = {}

    def fake_sort_remote(matrix, url=None):
        calls["matrix"] = matrix
        calls["url"] = url
        return np.array([4.0, 3.0, 2.0, 1.0]), np.array([[4.0, 3.0], [2.0, 1.0]])

    monkeypatch.setattr(integrated_app, "input_size", lambda prompt: 2)
    monkeypatch.setattr(integrated_app, "input_matrix", lambda m, n: sample)
    monkeypatch.setattr(integrated_app, "sort_remote", fake_sort_remote)

    assert integrated_app.run_once(url="http://test:1") is True
    assert calls["matrix"].tolist() == sample.tolist()
    assert calls["url"] == "http://test:1"
    out = capsys.readouterr().out
    assert "Исходная матрица" in out
    assert "Элементы по убыванию" in out
    assert "Результирующая матрица" in out


def test_run_once_handles_integration_error(monkeypatch, capsys, sample):
    def fail(matrix, url=None):
        raise ServiceUnavailableError("Сервис обработки недоступен")

    monkeypatch.setattr(integrated_app, "input_size", lambda prompt: 2)
    monkeypatch.setattr(integrated_app, "input_matrix", lambda m, n: sample)
    monkeypatch.setattr(integrated_app, "sort_remote", fail)

    assert integrated_app.run_once() is False
    out = capsys.readouterr().out
    assert "Ошибка интеграции: Сервис обработки недоступен" in out


def test_main_repeats_and_stops(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(integrated_app, "run_once", lambda: calls.append(1) or True)
    answers = iter(["y", "n"])
    monkeypatch.setattr("builtins.input", lambda *args: next(answers))

    integrated_app.main()

    assert len(calls) == 2
    out = capsys.readouterr().out
    assert "Работа программы завершена." in out
