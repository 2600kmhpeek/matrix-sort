# Интеграция модулей МатрСорт-16

## Архитектура взаимодействия

Три модуля связаны по клиент-серверной схеме через REST API (HTTP + JSON):

| Модуль | Файл | Роль |
|--------|------|------|
| Ввод | `src/matrix_sort.py` (input_size, input_matrix) | чтение и проверка матрицы в консоли |
| Обработка | `src/service.py` + `sort_desc` | REST-сервис сортировки |
| Вывод | `src/matrix_sort.py` (format_matrix) | форматирование результата |
| Клиент | `src/client.py` | передаёт данные в сервис, обрабатывает ошибки |
| Приложение | `src/integrated_app.py` | собирает всё в единый сценарий |

## Поток данных

ввод m, n и матрицы -> `sort_remote()` -> `POST /api/sort` (JSON) -> `sort_desc` -> JSON-ответ -> `format_matrix` -> вывод

## Протокол

Эндпоинты: `GET /api/health`, `POST /api/sort`. Заголовок `X-API-Version` задаёт версию API (текущая 1.0).

Запрос:
```json
{"matrix": [[1, 2, 3], [4, 5, 6]]}
```
Успешный ответ (200):
```json
{"status": "ok", "version": "1.0", "rows": 2, "cols": 3,
 "sorted_flat": [6, 5, 4, 3, 2, 1],
 "sorted_matrix": [[6, 5, 4], [3, 2, 1]]}
```
Ошибка (400/409):
```json
{"status": "error", "code": "INVALID_MATRIX", "message": "Строки матрицы имеют разную длину"}
```

Коды ошибок: MISSING_FIELD, INVALID_MATRIX, INVALID_VALUE, TOO_LARGE, BAD_JSON (400), VERSION_CONFLICT (409).

## Сопоставление данных

| Источник (модуль ввода) | JSON-поле | Приёмник (обработка) |
|-------------------------|-----------|----------------------|
| `np.ndarray` m x n | `matrix` (список списков) | `np.ndarray` float |
| результат `sort_desc`: flat | `sorted_flat` | `np.ndarray` для вывода |
| результат `sort_desc`: matrix | `sorted_matrix` | `np.ndarray` для `format_matrix` |
| `matrix.shape` | `rows`, `cols` | контроль размерности |

Нормализация: все числа приводятся к float; `ndarray` -> `list` через `tolist()`.

## Запуск

```bash
python -m src.service            # терминал 1: сервис
python -m src.integrated_app     # терминал 2: клиентское приложение
```
