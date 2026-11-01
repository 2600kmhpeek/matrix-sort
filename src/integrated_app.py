"""Интегрированное приложение: ввод -> REST-сервис обработки -> вывод."""
from src.client import DEFAULT_URL, IntegrationError, sort_remote
from src.matrix_sort import format_matrix, input_matrix, input_size


def run_once(url=DEFAULT_URL):
    """Один проход: ввод, обращение к сервису, вывод. Возвращает True при успехе."""
    m = input_size("Строк m: ")
    n = input_size("Столбцов n: ")
    matrix = input_matrix(m, n)
    try:
        sorted_flat, result = sort_remote(matrix, url=url)
    except IntegrationError as exc:
        print(f"Ошибка интеграции: {exc}")
        return False
    print("\nИсходная матрица:\n" + format_matrix(matrix))
    print("\nЭлементы по убыванию:\n" + format_matrix(sorted_flat))
    print("\nРезультирующая матрица:\n" + format_matrix(result))
    return True


def main():
    print("Расположение элементов матрицы m x n по убыванию (через REST-сервис)\n")
    while True:
        run_once()
        if input("\nПродолжить? (Y/n): ").strip().lower() != "y":
            print("Работа программы завершена.")
            break
        print()


if __name__ == "__main__":
    main()
