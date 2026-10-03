from unittest.mock import patch

import numpy as np

from src.matrix_sort import (format_matrix, input_matrix, input_size,
                             sort_desc)


def test_basic_matrix():
    flat, result = sort_desc(np.array([[1.0, 2, 3], [4, 5, 6]]))
    assert flat.tolist() == [6, 5, 4, 3, 2, 1]
    assert result.tolist() == [[6, 5, 4], [3, 2, 1]]


def test_negative_and_fractional():
    flat, _ = sort_desc(np.array([[-1.5, 3.2], [0, -2.1]]))
    assert flat.tolist() == [3.2, 0, -1.5, -2.1]


def test_all_equal():
    flat, _ = sort_desc(np.array([[5.0, 5, 5, 5]]))
    assert flat.tolist() == [5, 5, 5, 5]


def test_column_vector():
    flat, result = sort_desc(np.array([[2.0], [8], [-3]]))
    assert flat.tolist() == [8, 2, -3]
    assert result.shape == (3, 1)


def test_single_element():
    flat, result = sort_desc(np.array([[7.0]]))
    assert flat.tolist() == [7]
    assert result.shape == (1, 1)


def test_all_negative():
    matrix = np.array([[-5.0, -1, -3], [-9, -2, -4], [-7, -6, -8]])
    flat, _ = sort_desc(matrix)
    assert flat.tolist() == [-1, -2, -3, -4, -5, -6, -7, -8, -9]


def test_larger_random_matrix():
    matrix = np.random.default_rng(42).uniform(-100, 100, size=(5, 5))
    flat, result = sort_desc(matrix)
    assert len(flat) == 25
    assert all(flat[i] >= flat[i + 1] for i in range(24))
    assert sorted(flat) == sorted(matrix.flatten())
    assert result.shape == (5, 5)


def test_input_size_repeats_until_valid():
    with patch("builtins.input", side_effect=["abc", "0", "-2", "4"]):
        assert input_size("n: ") == 4


def test_input_matrix_valid():
    with patch("builtins.input", side_effect=["1 2 3", "4 5 6"]):
        assert input_matrix(2, 3).tolist() == [[1, 2, 3], [4, 5, 6]]


def test_input_matrix_rejects_letters():
    with patch("builtins.input", side_effect=["a b", "1 2"]):
        assert input_matrix(1, 2).tolist() == [[1, 2]]


def test_input_matrix_rejects_wrong_count():
    with patch("builtins.input", side_effect=["1 2", "1 2 3"]):
        assert input_matrix(1, 3).tolist() == [[1, 2, 3]]


def test_format_matrix_uses_three_decimals():
    text = format_matrix(np.array([[1.0, 2.5]]))
    assert "1.000" in text and "2.500" in text


def test_input_matrix_rejects_nan_and_inf():
    with patch("builtins.input", side_effect=["nan 1", "inf 2", "3 4"]):
        assert input_matrix(1, 2).tolist() == [[3, 4]]
