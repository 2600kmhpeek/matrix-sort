"""Модульные тесты модуля обработки (service.py).

Применены методы «чёрного ящика» (эквивалентное разбиение и анализ
граничных значений) и элементы «белого ящика» (покрытие решений и условий
функции validate_matrix).
"""
import pytest

from src import service
from src.service import MAX_ELEMENTS, app, validate_matrix


@pytest.fixture
def api():
    return app.test_client()


class TestValidateMatrix:
    """Классы эквивалентности и граничные значения входных данных."""

    def test_valid_integer_matrix(self):
        matrix, problem = validate_matrix({"matrix": [[1, 2], [3, 4]]})
        assert problem is None
        assert matrix.shape == (2, 2)
        assert matrix.dtype == float

    def test_valid_fractional_and_negative(self):
        matrix, problem = validate_matrix({"matrix": [[-1.5, 0.0], [2.25, -3]]})
        assert problem is None
        assert matrix.tolist() == [[-1.5, 0.0], [2.25, -3.0]]

    def test_valid_single_element_boundary(self):
        matrix, problem = validate_matrix({"matrix": [[7]]})
        assert problem is None
        assert matrix.shape == (1, 1)

    def test_valid_column_vector(self):
        matrix, problem = validate_matrix({"matrix": [[1], [2], [3]]})
        assert problem is None
        assert matrix.shape == (3, 1)

    def test_boundary_max_size_allowed(self):
        rows = [[1.0] * 100 for _ in range(MAX_ELEMENTS // 100)]
        matrix, problem = validate_matrix({"matrix": rows})
        assert problem is None
        assert matrix.size == MAX_ELEMENTS
        assert matrix.shape == (100, 100)

    def test_boundary_max_size_exceeded(self):
        rows = [[1.0] * 101 for _ in range(MAX_ELEMENTS // 100)]
        matrix, problem = validate_matrix({"matrix": rows})
        assert matrix is None
        assert problem[0] == "TOO_LARGE"

    def test_missing_matrix_field(self):
        matrix, problem = validate_matrix({"data": [[1]]})
        assert matrix is None
        assert problem == ("MISSING_FIELD", "Поле 'matrix' обязательно")

    def test_body_is_not_object(self):
        matrix, problem = validate_matrix([[1, 2]])
        assert matrix is None
        assert problem[0] == "MISSING_FIELD"

    @pytest.mark.parametrize("rows", [[], "abc", 5, None])
    def test_rows_not_nonempty_list(self, rows):
        matrix, problem = validate_matrix({"matrix": rows})
        assert matrix is None
        assert problem[0] == "INVALID_MATRIX"

    @pytest.mark.parametrize("rows", [[[]], [[1], []], ["12"]])
    def test_row_is_not_nonempty_list(self, rows):
        matrix, problem = validate_matrix({"matrix": rows})
        assert matrix is None
        assert problem[0] == "INVALID_MATRIX"

    def test_ragged_rows(self):
        matrix, problem = validate_matrix({"matrix": [[1, 2], [3]]})
        assert matrix is None
        assert problem[0] == "INVALID_MATRIX"

    @pytest.mark.parametrize("value", ["a", None, True, False, [1]])
    def test_element_is_not_number(self, value):
        matrix, problem = validate_matrix({"matrix": [[1, value]]})
        assert matrix is None
        assert problem[0] == "INVALID_VALUE"

    @pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
    def test_non_finite_values_rejected(self, value):
        matrix, problem = validate_matrix({"matrix": [[value]]})
        assert matrix is None
        assert problem[0] == "INVALID_VALUE"


class TestSortEndpoint:
    """Тесты REST-интерфейса модуля обработки."""

    def test_health(self, api):
        resp = api.get("/api/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok", "version": service.API_VERSION}

    def test_sort_returns_flat_and_matrix(self, api):
        resp = api.post("/api/sort", json={"matrix": [[1, 2, 3], [4, 5, 6]]})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "ok"
        assert body["rows"] == 2 and body["cols"] == 3
        assert body["sorted_flat"] == [6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
        assert body["sorted_matrix"] == [[6.0, 5.0, 4.0], [3.0, 2.0, 1.0]]

    def test_sort_error_format(self, api):
        resp = api.post("/api/sort", json={"matrix": [[1, 2], [3]]})
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["status"] == "error"
        assert set(body) == {"status", "code", "message"}

    def test_bad_json(self, api):
        resp = api.post("/api/sort", data="{не json", content_type="application/json")
        assert resp.status_code == 400
        assert resp.get_json()["code"] == "BAD_JSON"

    def test_version_major_conflict(self, api):
        resp = api.post("/api/sort", json={"matrix": [[1]]},
                        headers={"X-API-Version": "2.0"})
        assert resp.status_code == 409
        assert resp.get_json()["code"] == "VERSION_CONFLICT"

    def test_version_same_major_accepted(self, api):
        resp = api.post("/api/sort", json={"matrix": [[1]]},
                        headers={"X-API-Version": "1.9"})
        assert resp.status_code == 200

    def test_version_header_omitted(self, api):
        resp = api.post("/api/sort", json={"matrix": [[1]]})
        assert resp.status_code == 200

    def test_max_size_exceeded_over_http(self, api):
        rows = [[1.0] * 101 for _ in range(MAX_ELEMENTS // 100)]
        resp = api.post("/api/sort", json={"matrix": rows})
        assert resp.status_code == 400
        assert resp.get_json()["code"] == "TOO_LARGE"
