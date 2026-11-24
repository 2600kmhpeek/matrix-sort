# План тестирования и результаты

Документ описывает тестирование проекта «МатрСорт-16» в ЛР №4.
Целевое покрытие по варианту 16 — не менее 70 %, фактически достигнуто 90 %.

## 1. Объект и уровни тестирования

| Уровень | Что проверяется | Файлы тестов |
|---------|-----------------|--------------|
| Модульное | `matrix_sort.py`, `service.py`, `client.py`, `integrated_app.py` по отдельности | `test_matrix_sort.py`, `test_service.py`, `test_client.py`, `test_integrated_app.py` |
| Интеграционное | взаимодействие клиента, REST-сервиса и модуля вывода по HTTP | `test_integration.py` |
| Регрессионное | ранее найденные дефекты не возвращаются | `test_regression.py` |

Виды: функциональное, регрессионное. Подходы: «чёрный ящик» (эквивалентное
разбиение, граничные значения) и «белый ящик» (покрытие решений, условий,
комбинаторное покрытие условий).

## 2. Метод «чёрного ящика»: эквивалентное разбиение

### 2.1. Модуль ввода (`input_size`, `input_matrix`)

| Класс | Входные данные | Ожидаемое поведение | Тест |
|-------|----------------|---------------------|------|
| Корректный | положительное целое (`1`, `100`) | значение принимается | `test_input_size_accepts_positive` |
| Некорректный | `0`, отрицательное, текст | повторный запрос | `test_input_size_repeats_until_valid` |
| Корректный | ровно `n` чисел в строке | строка принимается | `test_input_matrix_valid` |
| Некорректный | буквы вместо чисел | повторный запрос строки | `test_input_matrix_rejects_letters` |
| Некорректный | чисел меньше или больше `n` | повторный запрос строки | `test_input_matrix_rejects_wrong_count` |
| Некорректный | `nan`, `inf` | повторный запрос строки | `test_input_matrix_rejects_nan_and_inf` |

### 2.2. Модуль обработки (`validate_matrix`)

| Класс | Входные данные | Код ошибки | Тест |
|-------|----------------|-----------|------|
| Корректный | целые и дробные числа, в т. ч. отрицательные | — | `test_valid_*` |
| Некорректный | нет поля `matrix` | `MISSING_FIELD` | `test_missing_matrix_field` |
| Некорректный | матрица не список / пустая | `INVALID_MATRIX` | `test_rows_not_nonempty_list` |
| Некорректный | пустая строка, строка не список | `INVALID_MATRIX` | `test_row_is_not_nonempty_list` |
| Некорректный | строки разной длины | `INVALID_MATRIX` | `test_ragged_rows` |
| Некорректный | строка, `None`, `bool`, список | `INVALID_VALUE` | `test_element_is_not_number` |
| Некорректный | `nan`, `inf`, `-inf` | `INVALID_VALUE` | `test_non_finite_values_rejected` |
| Некорректный | больше `MAX_ELEMENTS` | `TOO_LARGE` | `test_boundary_max_size_exceeded` |

### 2.3. Клиент (`sort_remote`, `_parse_response`)

| Класс ответа сервиса | Ожидаемое исключение | Тест |
|----------------------|----------------------|------|
| 200, корректный JSON | нет, возвращаются массивы NumPy | `test_success_returns_numpy` |
| 400 | `InvalidDataError` | `test_http_400_raises_invalid_data` |
| 409 | `VersionConflictError` | `test_http_409_raises_version_conflict` |
| 500 | `IntegrationError` | `test_http_500_raises_integration_error` |
| не JSON | `IntegrationError` | `test_non_json_response_raises_integration_error` |
| таймаут / нет соединения | `ServiceTimeoutError` / `ServiceUnavailableError` после повторов | `test_timeout_*`, `test_connection_*` |

### 2.4. Интегрированное приложение (`run_once`, `main`)

| Класс | Входные данные | Ожидаемый результат | Тест |
|-------|----------------|---------------------|------|
| Успешный сценарий | матрица 2 × 2, сервис доступен | `True`, три блока вывода | `test_run_once_success` |
| Отказ сервиса | `ServiceUnavailableError` | `False`, сообщение об ошибке | `test_run_once_handles_integration_error` |
| Цикл работы | ответы `y`, `n` | два прохода и завершение | `test_main_repeats_and_stops` |

## 3. Метод «чёрного ящика»: анализ граничных значений

| Граница | Значение на границе | Значение за границей | Тест |
|---------|---------------------|----------------------|------|
| Размерность | 1 × 1 | 0 (недопустимо) | `test_single_element`, `test_valid_single_element_boundary` |
| Число элементов | 10 000 (`100 × 100`) — допустимо | 10 100 (`101 × 100`) — `TOO_LARGE` | `test_boundary_max_size_allowed`, `test_boundary_max_size_exceeded` |
| Размерность ввода | 1 | 0, −2 | `test_input_size_accepts_positive`, `test_input_size_repeats_until_valid` |
| Повторы клиента | `retries = 0` — одна попытка | `retries = 2` — три попытки | `test_no_retries_single_attempt`, `test_timeout_retries_then_raises` |
| Версия API | `1.9` — совместима | `2.0` — конфликт | `test_version_same_major_accepted`, `test_version_major_conflict` |
| Длина вывода | 1 000 элементов | 1 001 и 1 200 элементов — без обрезки | `test_long_flat_output_is_not_truncated`, `test_large_matrix_output_is_not_truncated` |

## 4. Метод «белого ящика»

### 4.1. Покрытие решений

| Решение | Ветви | Чем покрыты |
|---------|-------|-------------|
| `if value > 0` (`input_size`) | True / False | `test_input_size_accepts_positive`, `test_input_size_repeats_until_valid` |
| `if len(row) != n or not np.all(np.isfinite(row))` | True / False | корректная строка, неверное число элементов, `nan`/`inf` |
| `if not isinstance(data, dict) or "matrix" not in data` | True / False | `test_body_is_not_object`, `test_missing_matrix_field`, корректные тесты |
| `if not isinstance(rows, list) or not rows` | True / False | `test_rows_not_nonempty_list`, корректные тесты |
| `if width is None` / `elif len(row) != width` | True / False | первая строка, ровные и рваные строки |
| `if isinstance(x, bool) or not isinstance(x, (int, float))` | True / False | `test_element_is_not_number`, корректные тесты |
| `if not math.isfinite(x)` | True / False | `test_non_finite_values_rejected`, корректные тесты |
| `if len(rows) * width > MAX_ELEMENTS` | True / False | граница 10 000 и 10 100 |
| `try/except ValueError` в `input_size` и `input_matrix` | True / False | текст вместо числа, корректный ввод |
| `except requests.exceptions.Timeout` / `ConnectionError` | True / False | `test_timeout_*`, `test_connection_*`, `test_retry_then_success` |
| `if resp.status_code == 400 / == 409 / != 200` | True / False | `test_http_400`, `test_http_409`, `test_http_500` |
| `if not isinstance(body, dict)` | True / False | `test_client_rejects_non_object_json`, корректный ответ |
| `except KeyError` | True / False | `test_client_rejects_response_without_fields`, корректный ответ |

### 4.2. Покрытие условий

Для каждого простого условия проверены оба исхода. Пример для
`not isinstance(rows, list) or not rows`: `"abc"` (первое истинно),
`[]` (первое ложно, второе истинно), `[[1]]` (оба ложны). Аналогично для
`isinstance(x, bool) or not isinstance(x, (int, float))`: `True`, `"a"`,
`1.5`. Для `len(row) != n or not np.all(np.isfinite(row))`: корректная
строка, строка другой длины, строка с `nan`.

### 4.3. Комбинаторное покрытие условий

| Условие 1 | Условие 2 | Набор данных | Результат |
|-----------|-----------|--------------|-----------|
| элемент — `bool` (T) | — | `True` | `INVALID_VALUE` |
| элемент — не число (T) | — | `"a"`, `None`, `[1]` | `INVALID_VALUE` |
| элемент — число (F) | не конечное (T) | `nan`, `inf`, `-inf` | `INVALID_VALUE` |
| элемент — число (F) | конечное (F) | `1.5`, `-3`, `0` | корректно |
| длина строки верна (F) | все числа конечны (F) | `1 2 3` при `n = 3` | строка принята |
| длина строки неверна (T) | — | `1 2` при `n = 3` | повторный ввод |
| длина строки верна (F) | есть `nan` (T) | `nan 1 2` | повторный ввод |

## 5. Тестовые модули

| Файл | Число тестов | Что проверяет |
|------|--------------|---------------|
| `tests/test_matrix_sort.py` | 22 (17 функций) | ввод, сортировка, форматирование |
| `tests/test_service.py` | 32 (21 функция) | валидация и REST-интерфейс |
| `tests/test_client.py` | 11 | разбор ответов, повторы, исключения |
| `tests/test_integrated_app.py` | 3 | сценарий приложения и цикл работы |
| `tests/test_integration.py` | 19 (15 функций) | взаимодействие по HTTP |
| `tests/test_regression.py` | 10 | защита от возврата дефектов |
| **Итого** | **97** (с учётом параметризации) | |

## 6. Запуск

```bash
python -m pytest tests/ -v --cov=src --cov-branch --cov-report=term-missing
python -m pytest tests/test_integration.py -v --cov=src
python -m pytest tests/test_regression.py -v
flake8 src tests --max-line-length=100 --statistics
```

## 7. Результаты

```
============================== 97 passed in 0.74s ==============================

Name                    Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------
src/__init__.py             0      0      0      0   100%
src/client.py              46      0     10      0   100%
src/integrated_app.py      25      1      4      1    93%   33
src/matrix_sort.py         47     14     10      1    70%   46-58, 62
src/service.py             50      1     28      1    97%   75
-------------------------------------------------------------------
TOTAL                     168     16     52      3    90%
```

Покрытие 90 % при целевом 70 %. Непокрытыми остались строки интерактивного
цикла `main()` в `matrix_sort.py` и ветка запуска сервиса
`if __name__ == "__main__"`.

## 8. Дефекты

Найдено два дефекта, оба исправлены и закрыты регрессионными тестами.
Подробные баг-репорты — в `docs/bug_reports.md`.

| № | Дефект | Тяжесть | Статус |
|---|--------|---------|--------|
| D1 | Вывод матрицы более 1000 элементов обрезается многоточием | средняя | исправлен |
| D2 | Клиент падает с `AttributeError`/`KeyError` при неверной структуре ответа | высокая | исправлен |

## 9. Тестирование интеграции

Интеграционные тесты из ЛР №3 перезапущены: 19 проверок, все пройдены.
HTTP-сервис поднимается в отдельном потоке на свободном порту, поэтому
тесты не зависят от внешнего окружения. Сценарии и результаты —
в `docs/integration_test.md`.

## 10. Регрессионное тестирование

`tests/test_regression.py` содержит 10 тестов: 2 воспроизводят дефекты D1 и
D2, 8 закрепляют исправления ЛР №2–ЛР №3 (`nan`/`inf`, рваные строки,
`bool`, конфликт версий, повторный ввод, базовая сортировка). Запуск
автоматизирован в задании `regression` рабочего процесса
`.github/workflows/testing.yml` после успешного прохождения модульных тестов.

## 11. CI

Рабочий процесс `Testing` (`.github/workflows/testing.yml`) запускается при
push и pull request в `main` и `develop`:

1. установка зависимостей;
2. `flake8 src tests --max-line-length=100`;
3. модульные и интеграционные тесты с покрытием и порогом 80 %;
4. отдельное задание регрессионных тестов.

Порог CI (80 %) выше целевого по варианту (70 %), что не даёт покрытию
снизиться при доработках.
