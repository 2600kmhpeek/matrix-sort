"""Интеграционные тесты: клиент <-> REST-сервис <-> форматирование вывода."""
import threading

import numpy as np
import pytest
import requests
from werkzeug.serving import make_server

from src import client, integrated_app
from src.matrix_sort import format_matrix
from src.service import app


@pytest.fixture(scope="module")
def url():
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture
def api():
    return app.test_client()


def test_health(api):
    assert api.get("/api/health").get_json()["status"] == "ok"


def test_sort_basic_over_http(url):
    flat, matrix = client.sort_remote([[1, 2, 3], [4, 5, 6]], url=url)
    assert flat.tolist() == [6, 5, 4, 3, 2, 1]
    assert matrix.tolist() == [[6, 5, 4], [3, 2, 1]]


def test_sort_negative_and_fractional(url):
    flat, _ = client.sort_remote([[-1.5, 2.25], [0, -3]], url=url)
    assert flat.tolist() == [2.25, 0, -1.5, -3]


def test_single_element(url):
    flat, matrix = client.sort_remote([[7]], url=url)
    assert flat.tolist() == [7] and matrix.shape == (1, 1)


def test_column_vector_keeps_shape(url):
    _, matrix = client.sort_remote([[1], [3], [2]], url=url)
    assert matrix.tolist() == [[3], [2], [1]]


def test_all_equal(url):
    flat, _ = client.sort_remote([[2, 2], [2, 2]], url=url)
    assert flat.tolist() == [2, 2, 2, 2]


def test_service_unavailable():
    with pytest.raises(client.ServiceUnavailableError):
        client.sort_remote([[1]], url="http://127.0.0.1:1", retries=0)


def test_timeout(monkeypatch):
    def fake_post(*args, **kwargs):
        raise requests.exceptions.Timeout()
    monkeypatch.setattr(client.requests, "post", fake_post)
    with pytest.raises(client.ServiceTimeoutError):
        client.sort_remote([[1]], retries=1)


@pytest.mark.parametrize("body", [
    {"matrix": []},
    {"matrix": [[1, 2], [3]]},
    {"matrix": [[1, "a"]]},
    {"matrix": [[1, True]]},
    {"data": [[1]]},
])
def test_invalid_data_rejected(api, body):
    resp = api.post("/api/sort", json=body)
    assert resp.status_code == 400
    assert resp.get_json()["status"] == "error"


def test_nan_inf_rejected(api):
    resp = api.post("/api/sort", data='{"matrix": [[1, NaN]]}',
                    content_type="application/json")
    assert resp.status_code == 400


def test_bad_json(api):
    resp = api.post("/api/sort", data="не json", content_type="application/json")
    assert resp.get_json()["code"] == "BAD_JSON"


def test_version_conflict(api):
    resp = api.post("/api/sort", json={"matrix": [[1]]},
                    headers={"X-API-Version": "2.0"})
    assert resp.status_code == 409
    assert resp.get_json()["code"] == "VERSION_CONFLICT"


def test_client_maps_400_to_invalid_data(url, monkeypatch):
    monkeypatch.setattr(client.np, "asarray", lambda m, dtype=None: np.array([]))
    with pytest.raises(client.InvalidDataError):
        client.sort_remote([[1]], url=url, retries=0)


def test_full_scenario(url, monkeypatch, capsys):
    answers = iter(["2", "2", "1 4", "3 2", "н"])
    monkeypatch.setattr("builtins.input", lambda *a: next(answers))
    assert integrated_app.run_once(url=url) is True
    out = capsys.readouterr().out
    expected = format_matrix(np.array([[4, 3], [2, 1]], dtype=float))
    assert expected in out


def test_app_survives_unavailable_service(monkeypatch, capsys):
    answers = iter(["1", "1", "5"])
    monkeypatch.setattr("builtins.input", lambda *a: next(answers))
    assert integrated_app.run_once(url="http://127.0.0.1:1") is False
    assert "Ошибка интеграции" in capsys.readouterr().out
