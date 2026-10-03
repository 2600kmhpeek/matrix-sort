# План тестирования

Тесты расположены в `tests/test_matrix_sort.py`, запуск: `python -m pytest -v`.
Статический анализ: `flake8 src tests --max-line-length=100`.
Обе проверки выполняются автоматически в GitHub Actions (`.github/workflows/ci.yml`).

| № ТЗ | Тест | Входные данные | Ожидаемый результат |
|------|------|----------------|---------------------|
| 1 | `test_basic_matrix` | 1 2 3 / 4 5 6 | 6 5 4 3 2 1 |
| 2 | `test_negative_and_fractional` | -1.5 3.2 / 0 -2.1 | 3.2 0 -1.5 -2.1 |
| 3 | `test_all_equal` | 5 5 5 5 | 5 5 5 5 |
| 4 | `test_column_vector` | 2 / 8 / -3 | 8 2 -3, форма (3, 1) |
| 5 | `test_single_element` | 7 | 7 |
| 6 | `test_input_matrix_rejects_letters` | «a b», затем «1 2» | повторный запрос строки |
| 7 | `test_input_size_repeats_until_valid` | abc, 0, -2, 4 | возвращается 4 |
| 8 | `test_input_matrix_rejects_wrong_count` | «1 2», затем «1 2 3» | повторный запрос строки |
| 9 | `test_all_negative` | 3 × 3, все отрицательные | -1 … -9 |
| 10 | `test_larger_random_matrix` | 5 × 5, случайные | 25 элементов по убыванию |
| — | `test_format_matrix_uses_three_decimals` | 1.0, 2.5 | «1.000», «2.500» |

Номера соответствуют плану тестирования из технического задания (ЛР №1).
