# Тестирование интеграции

Запуск: `python -m pytest tests/test_integration.py -v --cov=src`

| № | Сценарий | Ожидаемый результат | Тест |
|---|----------|---------------------|------|
| 1 | Проверка работоспособности сервиса | 200, status ok | test_health |
| 2 | Нормальная матрица 2x3 по HTTP | 6 5 4 3 2 1 | test_sort_basic_over_http |
| 3 | Отрицательные и дробные числа | корректный порядок | test_sort_negative_and_fractional |
| 4 | Матрица 1x1 | без ошибок, форма 1x1 | test_single_element |
| 5 | Вектор-столбец | форма n x 1 сохраняется | test_column_vector_keeps_shape |
| 6 | Все элементы равны | без ошибок | test_all_equal |
| 7 | Сервис недоступен | ServiceUnavailableError | test_service_unavailable |
| 8 | Таймаут | ServiceTimeoutError | test_timeout |
| 9 | Некорректные данные (пустая, рваная, строки, bool, нет поля) | 400 + status error | test_invalid_data_rejected |
| 10 | nan в JSON | 400 | test_nan_inf_rejected |
| 11 | Не JSON | BAD_JSON | test_bad_json |
| 12 | Версия API 2.0 | 409 VERSION_CONFLICT | test_version_conflict |
| 13 | Клиент получает 400 | InvalidDataError | test_client_maps_400_to_invalid_data |
| 14 | Полный сценарий ввод -> сервис -> вывод | вывод совпадает с format_matrix | test_full_scenario |
| 15 | Приложение при недоступном сервисе | сообщение об ошибке, без падения | test_app_survives_unavailable_service |

Результат:
 @rlexin  python -m pytest tests/test_integration.py -v --cov=src
==================================== test session starts =====================================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0 -- /usr/bin/python
cachedir: .pytest_cache
rootdir: /home/rlexin/Документы/лабы/кургасов/matrix-sort
plugins: anyio-4.15.1, cov-7.1.0
collected 19 items                                                                           

tests/test_integration.py::test_health PASSED                                          [  5%]
tests/test_integration.py::test_sort_basic_over_http PASSED                            [ 10%]
tests/test_integration.py::test_sort_negative_and_fractional PASSED                    [ 15%]
tests/test_integration.py::test_single_element PASSED                                  [ 21%]
tests/test_integration.py::test_column_vector_keeps_shape PASSED                       [ 26%]
tests/test_integration.py::test_all_equal PASSED                                       [ 31%]
tests/test_integration.py::test_service_unavailable PASSED                             [ 36%]
tests/test_integration.py::test_timeout PASSED                                         [ 42%]
tests/test_integration.py::test_invalid_data_rejected[body0] PASSED                    [ 47%]
tests/test_integration.py::test_invalid_data_rejected[body1] PASSED                    [ 52%]
tests/test_integration.py::test_invalid_data_rejected[body2] PASSED                    [ 57%]
tests/test_integration.py::test_invalid_data_rejected[body3] PASSED                    [ 63%]
tests/test_integration.py::test_invalid_data_rejected[body4] PASSED                    [ 68%]
tests/test_integration.py::test_nan_inf_rejected PASSED                                [ 73%]
tests/test_integration.py::test_bad_json PASSED                                        [ 78%]
tests/test_integration.py::test_version_conflict PASSED                                [ 84%]
tests/test_integration.py::test_client_maps_400_to_invalid_data PASSED                 [ 89%]
tests/test_integration.py::test_full_scenario PASSED                                   [ 94%]
tests/test_integration.py::test_app_survives_unavailable_service PASSED                [100%]

======================================= tests coverage =======================================
______________________ coverage: platform linux, python 3.14.7-final-0 _______________________

Name                    Stmts   Miss  Cover
-------------------------------------------
src/__init__.py             0      0   100%
src/client.py              39      4    90%
src/integrated_app.py      25      8    68%
src/matrix_sort.py         46     20    57%
src/service.py             50      3    94%
-------------------------------------------
TOTAL                     160     35    78%
===================================== 19 passed in 0.68s =====================================
