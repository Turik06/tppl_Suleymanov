import runpy
import sys
import warnings
from unittest.mock import patch
import pytest

from postfix_notation.main import (
    CaringStackMachineError,
    to_int_if_whole,
    format_num,
    validate_number,
    parse_number,
    evaluate_postfix,
    main,
)


class TestArithmeticOperations:
    @pytest.mark.parametrize(
        "expression, expected",
        [
            ("2 3 +", 5),
            ("10 4 -", 6),
            ("3 5 *", 15),
            ("15 3 /", 5),
            ("7 2 /", 3.5),
            ("-5 3 +", -2),
            ("2.5 1.5 +", 4),
            ("5.5 2.2 -", 3.3),
        ],
        ids=[
            "addition",
            "subtraction",
            "multiplication",
            "integer_division",
            "float_division",
            "negative_numbers",
            "float_to_int_sum",
            "float_subtraction",
        ],
    )
    def test_arithmetic_results(self, expression, expected):
        result = evaluate_postfix(expression, verbose=False)
        assert result == pytest.approx(expected, 0.0001)


class TestTildeOperator:
    @pytest.mark.parametrize(
        "expression, expected",
        [
            ("5 3 ~", 2),
            ("3 5 ~", 2),
            ("10 10 ~", 0),
            ("0 4 ~", 16),
            ("4 0 ~", 16),
            ("1 2 0 ~", 9),
            ("0 0 ~", 0),
        ],
        ids=[
            "both_non_zero_positive_diff",
            "both_non_zero_negative_diff",
            "both_non_zero_equal",
            "first_operand_zero",
            "second_operand_zero",
            "zero_with_larger_stack",
            "both_operands_zero",
        ],
    )
    def test_tilde_results(self, expression, expected):
        result = evaluate_postfix(expression, verbose=False)
        assert result == expected

    @pytest.mark.parametrize(
        "expression, expected",
        [
            ("3 0 4 ~ 2 ~", 47),
            ("2 2 + 4 - 4 ~ 2 3 * +", 22),
        ],
        ids=["task_example_1", "task_example_2"],
    )
    def test_task_examples(self, expression, expected):
        result = evaluate_postfix(expression, verbose=True)
        assert result == expected


class TestValidationAndErrors:
    @pytest.mark.parametrize(
        "expression",
        ["", "   "],
        ids=["empty_string", "spaces_only"],
    )
    def test_empty_expression(self, expression):
        with pytest.raises(CaringStackMachineError, match="Выражение не должно быть пустым"):
            evaluate_postfix(expression)

    @pytest.mark.parametrize(
        "expression, op",
        [
            ("+", "+"),
            ("1 +", "+"),
            ("-", "-"),
            ("*", "*"),
            ("/", "/"),
            ("~", "~"),
            ("5 ~", "~"),
        ],
        ids=[
            "add_no_operands",
            "add_single_operand",
            "sub_no_operands",
            "mul_no_operands",
            "div_no_operands",
            "tilde_no_operands",
            "tilde_single_operand",
        ],
    )
    def test_insufficient_operands(self, expression, op):
        with pytest.raises(CaringStackMachineError, match="нужно минимум 2 операнда"):
            evaluate_postfix(expression)

    def test_division_by_zero(self):
        with pytest.raises(CaringStackMachineError, match="Деление на ноль невозможно"):
            evaluate_postfix("10 0 /")

    def test_unknown_token(self):
        with pytest.raises(CaringStackMachineError, match="Неизвестный токен"):
            evaluate_postfix("2 3 ?")

    @pytest.mark.parametrize(
        "token",
        ["nan", "NaN", "inf", "INF", "-inf", "+inf"],
        ids=["nan_lower", "nan_mixed", "inf_lower", "inf_upper", "neg_inf", "pos_inf"],
    )
    def test_unsupported_special_tokens(self, token):
        with pytest.raises(CaringStackMachineError, match="не поддерживается"):
            parse_number(token)

    def test_extra_operands_in_stack(self):
        with pytest.raises(CaringStackMachineError, match="осталось 2 чисел"):
            evaluate_postfix("2 3 4 +")

    def test_overflow_arithmetic(self):
        class OverflowNum:
            def __add__(self, other):
                raise OverflowError()

        with patch("postfix_notation.main.parse_number", side_effect=[OverflowNum(), 2, None]):
            with pytest.raises(CaringStackMachineError, match="арифметическое переполнение"):
                evaluate_postfix("a b +", verbose=False)

    def test_overflow_tilde(self):
        with patch("builtins.sum", side_effect=OverflowError):
            with pytest.raises(CaringStackMachineError, match="переполнение"):
                evaluate_postfix("0 0 ~", verbose=False)


class TestHelperFunctions:
    def test_to_int_if_whole(self):
        assert to_int_if_whole(5.0) == 5
        assert isinstance(to_int_if_whole(5.0), int)
        assert to_int_if_whole(5.5) == 5.5
        assert to_int_if_whole(10) == 10

    def test_format_num(self):
        assert format_num(5) == "5"
        assert format_num(5.0) == "5"
        assert format_num(3.1400) == "3.14"
        assert format_num(3.14159) == "3.1416"

    def test_validate_number(self):
        validate_number(10)
        validate_number(3.14)
        with pytest.raises(CaringStackMachineError, match="Обнаружено некорректное значение"):
            validate_number(float("nan"))
        with pytest.raises(CaringStackMachineError, match="Обнаружено некорректное значение"):
            validate_number(float("inf"))

    def test_parse_number(self):
        assert parse_number("42") == 42
        assert parse_number("-7") == -7
        assert parse_number("3.5") == 3.5
        assert parse_number("abc") is None


class TestCLI:
    def test_cli_help(self, capsys):
        with patch.object(sys, "argv", ["main.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Использование:" in captured.out

    def test_cli_success(self, capsys):
        with patch.object(sys, "argv", ["main.py", "3", "0", "4", "~", "2", "~"]):
            main()
            captured = capsys.readouterr()
            assert "3 0 4 ~ 2 ~ = 47" in captured.out

    def test_cli_error(self, capsys):
        with patch.object(sys, "argv", ["main.py", "10", "0", "/"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Ошибка вычисления:" in captured.out

    def test_run_as_main(self, capsys):
        with patch.object(sys, "argv", ["main.py", "1", "2", "+"]):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                runpy.run_module("postfix_notation.main", run_name="__main__")
            captured = capsys.readouterr()
            assert "1 2 + = 3" in captured.out
