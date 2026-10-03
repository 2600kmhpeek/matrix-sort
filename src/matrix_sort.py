import numpy as np

PRECISION = 3  # количество знаков после запятой при выводе

def input_size(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
        except ValueError:
            pass
        print("Ошибка: введите положительное целое число.")


def input_matrix(m, n):
    print(f"Введите {m} строк(и) по {n} вещественных чисел через пробел:")
    rows = []
    while len(rows) < m:
        parts = input(f"Строка {len(rows) + 1}: ").split()
        try:
            row = list(map(float, parts))
            if len(row) != n:
                raise ValueError
            rows.append(row)
        except ValueError:
            print(f"Ошибка: нужно {n} вещественных чисел. Повторите ввод.")
    return np.array(rows)


def sort_desc(matrix):
    m, n = matrix.shape
    sorted_flat = np.sort(matrix.flatten())[::-1]
    return sorted_flat, sorted_flat.reshape(m, n)


def format_matrix(matrix):
    return np.array2string(matrix, precision=PRECISION, suppress_small=True,
                           floatmode="fixed")


def main():
    print("Расположение элементов вещественной матрицы m x n по убыванию (обход по строкам)\n")
    while True:
        m = input_size("Строк m: ")
        n = input_size("Столбцов n: ")
        matrix = input_matrix(m, n)
        sorted_flat, result = sort_desc(matrix)
        print("\nИсходная матрица:\n" + format_matrix(matrix))
        print("\nЭлементы по убыванию:\n" + format_matrix(sorted_flat))
        print("\nРезультирующая матрица:\n" + format_matrix(result))
        if input("\nПродолжить? (Y/n): ").strip().lower() != "y":
            print("Работа программы завершена.")
            break
        print()


if __name__ == "__main__":
    main()
