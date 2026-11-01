"""Модуль обработки как REST-сервис (Flask): сортировка матрицы по убыванию."""
import math

import numpy as np
from flask import Flask, jsonify, request

from src.matrix_sort import sort_desc

API_VERSION = "1.0"
MAX_ELEMENTS = 10000

app = Flask(__name__)


def error(code, message, status):
    """Единый формат ошибки: JSON с кодом и сообщением."""
    return jsonify({"status": "error", "code": code, "message": message}), status


def validate_matrix(data):
    """Проверяет тело запроса. Возвращает (matrix, None) или (None, (code, msg))."""
    if not isinstance(data, dict) or "matrix" not in data:
        return None, ("MISSING_FIELD", "Поле 'matrix' обязательно")
    rows = data["matrix"]
    if not isinstance(rows, list) or not rows:
        return None, ("INVALID_MATRIX", "Матрица должна быть непустым списком строк")
    width = None
    for row in rows:
        if not isinstance(row, list) or not row:
            return None, ("INVALID_MATRIX", "Каждая строка должна быть непустым списком")
        if width is None:
            width = len(row)
        elif len(row) != width:
            return None, ("INVALID_MATRIX", "Строки матрицы имеют разную длину")
        for x in row:
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                return None, ("INVALID_VALUE", "Элементы должны быть числами")
            if not math.isfinite(x):
                return None, ("INVALID_VALUE", "Значения nan и inf недопустимы")
    if len(rows) * width > MAX_ELEMENTS:
        return None, ("TOO_LARGE", "Превышен максимальный размер матрицы")
    return np.array(rows, dtype=float), None


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "version": API_VERSION})


@app.post("/api/sort")
def sort_endpoint():
    client_version = request.headers.get("X-API-Version", API_VERSION)
    if client_version.split(".")[0] != API_VERSION.split(".")[0]:
        return error("VERSION_CONFLICT",
                     f"Сервис поддерживает версию {API_VERSION}, получена {client_version}", 409)
    data = request.get_json(silent=True)
    if data is None:
        return error("BAD_JSON", "Тело запроса не является корректным JSON", 400)
    matrix, problem = validate_matrix(data)
    if problem:
        return error(problem[0], problem[1], 400)
    flat, sorted_matrix = sort_desc(matrix)
    m, n = matrix.shape
    return jsonify({
        "status": "ok",
        "version": API_VERSION,
        "rows": m,
        "cols": n,
        "sorted_flat": np.asarray(flat).tolist(),
        "sorted_matrix": np.asarray(sorted_matrix).tolist(),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
