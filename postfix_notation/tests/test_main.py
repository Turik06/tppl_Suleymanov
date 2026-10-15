import runpy
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
REPO_DIR = BASE_DIR.parent
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))

try:
    if Path.cwd().resolve() == BASE_DIR.resolve():
        import main as main_mod
    else:
        from postfix_notation import main as main_mod
except ModuleNotFoundError:
    try:
        import main as main_mod
    except ModuleNotFoundError:
        from postfix_notation import main as main_mod

BINARY_OPERATIONS = main_mod.BINARY_OPERATIONS
HELP_MESSAGE = main_mod.HELP_MESSAGE
calc_div = main_mod.calc_div
calc_mul = main_mod.calc_mul
calc_sub = main_mod.calc_sub
calc_sum = main_mod.calc_sum
calc_tilde = main_mod.calc_tilde
evaluate_expression = main_mod.evaluate_expression
format_result = main_mod.format_result
is_numeric = main_mod.is_numeric
main = main_mod.main
parse_token = main_mod.parse_token
to_int_if_whole = main_mod.to_int_if_whole


class TestHelpers:
    @pytest.mark.parametrize(
        "token, expected",
        [
            ("0", True),
            ("42", True),
            ("-15", True),
            ("3.14", True),
            ("-0.5", True),
            ("abc", False),
            ("nan", False),
            ("inf", False),
            ("-infinity", False),
            ("", False),
        ],
    )
    def test_is_numeric(self, token, expected):
        assert is_numeric(token) == expected

    @pytest.mark.parametrize(
        "val, expected, expected_type",
        [
            (5.0, 5, int),
            (5.25, 5.25, float),
            (10, 10, int),
            (-3.0, -3, int),
            (-3.14, -3.14, float),
        ],
    )
    def test_to_int_if_whole(self, val, expected, expected_type):
        res = to_int_if_whole(val)
        assert res == expected
        assert isinstance(res, expected_type)

    @pytest.mark.parametrize(
        "token, expected",
        [
            ("12", 12),
            ("3.5", 3.5),
            ("-42", -42),
            ("0.0", 0),
        ],
    )
    def test_parse_token(self, token, expected):
        assert parse_token(token) == expected

    @pytest.mark.parametrize(
        "val, expected",
        [
            (7.0, "7"),
            (7.5, "7.5"),
            (0, "0"),
            (-4.0, "-4"),
        ],
    )
    def test_format_result(self, val, expected):
        assert format_result(val) == expected


class TestOperations:
    @pytest.mark.parametrize(
        "op_func, x, y, expected",
        [
            (calc_sum, 2, 3, 5),
            (calc_sum, 2.5, 3.5, 6),
            (calc_sum, -5, 3, -2),
            (calc_sub, 10, 4, 6),
            (calc_sub, 4, 10, -6),
            (calc_sub, 5.5, 0.5, 5),
            (calc_mul, 3, 4, 12),
            (calc_mul, 2.5, 2, 5),
            (calc_mul, -2, 3, -6),
            (calc_div, 10, 2, 5),
            (calc_div, 7, 2, 3.5),
        ],
    )
    def test_binary_operations(self, op_func, x, y, expected):
        assert op_func(x, y) == expected

    def test_division_by_zero(self):
        with pytest.raises(ZeroDivisionError, match="Деление на ноль невозможно"):
            calc_div(5, 0)

    @pytest.mark.parametrize(
        "initial_stack, expected_stack",
        [
            ([10, 3, 8], [10, 5]),
            ([2, 5], [3]),
            ([3, 0, 4], [49]),
            ([0, 4], [16]),
            ([4, 0], [16]),
            ([2, 1, 5, 0], [64]),
            ([0, 0], [0]),
        ],
        ids=[
            "diff_positive",
            "diff_order_abs",
            "zero_operand_including_stack_and_operands",
            "zero_first_operand_sum_squared",
            "zero_second_operand_sum_squared",
            "zero_with_multi_element_stack",
            "both_zeros",
        ],
    )
    def test_calc_tilde_valid(self, initial_stack, expected_stack):
        assert calc_tilde(initial_stack) == expected_stack

    @pytest.mark.parametrize(
        "stack",
        [[], [1]],
        ids=["empty_stack", "single_element"],
    )
    def test_calc_tilde_insufficient_operands(self, stack):
        with pytest.raises(ValueError, match="требует не менее двух операндов"):
            calc_tilde(stack)


class TestEvaluation:
    @pytest.mark.parametrize(
        "expression, expected",
        [
            ("3 0 4 ~ 2 ~", 47),
            ("2 2 + 4 - 4 ~ 2 3 * +", 22),
            ("5 1 2 + 4 * + 3 -", 14),
            ("15 3 / 2 +", 7),
            ("4 2 / 2 /", 1),
            ("10 2 - 3 -", 5),
            ("2.5 1.5 +", 4),
            ("-5 3 +", -2),
        ],
        ids=[
            "task_case_1",
            "task_case_2",
            "combined_arithmetic",
            "div_and_add",
            "chained_division",
            "chained_subtraction",
            "float_conversion_to_int",
            "negative_arithmetic",
        ],
    )
    def test_evaluate_expression_valid(self, expression, expected):
        assert evaluate_expression(expression, verbose=False) == expected

    @pytest.mark.parametrize(
        "expression, exc_type, match",
        [
            ("   ", ValueError, "не должно быть пустым"),
            ("2 3 & +", ValueError, "Неизвестный токен в выражении"),
            ("2 +", ValueError, "требует не менее двух операндов"),
            ("~", ValueError, "требует не менее двух операндов"),
            ("1 2 3 +", ValueError, "должно остаться ровно одно число"),
            ("10 0 /", ZeroDivisionError, "Деление на ноль невозможно"),
            ("/home/user 2 +", ValueError, "похож на путь"),
        ],
        ids=[
            "empty",
            "unknown_op",
            "missing_operands_binary",
            "missing_operands_tilde",
            "stack_too_large_at_end",
            "div_zero",
            "expanded_tilde_path",
        ],
    )
    def test_evaluate_expression_errors(self, expression, exc_type, match):
        with pytest.raises(exc_type, match=match):
            evaluate_expression(expression, verbose=False)

    def test_verbose_output(self, capsys):
        res = evaluate_expression("2 3 +", verbose=True)
        assert res == 5
        captured = capsys.readouterr()
        assert "Шаг  1: токен '2' -> стек: [2]" in captured.out
        assert "Шаг  2: токен '3' -> стек: [2, 3]" in captured.out
        assert "Шаг  3: токен '+' -> стек: [5]" in captured.out


class TestCLI:
    @pytest.mark.parametrize(
        "args, expected_code, expected_output",
        [
            ([], 1, "Использование:"),
            (["-h"], 0, "Стековая машина"),
            (["--help"], 0, "Стековая машина"),
            (["3 0 4 ~ 2 ~"], 0, "3 0 4 ~ 2 ~ = 47"),
            (["3", "0", "4", "~", "2", "~"], 0, "3 0 4 ~ 2 ~ = 47"),
            (["2 2 + 4 - 4 ~ 2 3 * +"], 0, "2 2 + 4 - 4 ~ 2 3 * + = 22"),
            (["10 0 /"], 1, "Деление на ноль невозможно"),
            (["invalid_token"], 1, "Неизвестный токен в выражении"),
            (["/home/user", "2", "+"], 1, "похож на путь"),
        ],
        ids=[
            "no_args",
            "flag_h",
            "flag_help",
            "task_ex1_str",
            "task_ex1_tokens",
            "task_ex2",
            "div_by_zero",
            "invalid_tok",
            "path_expansion",
        ],
    )
    def test_main_cli_args(self, args, expected_code, expected_output, capsys):
        code = main(args)
        assert code == expected_code
        captured = capsys.readouterr()
        assert expected_output in (captured.out + captured.err)

    def test_main_default_sys_argv(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["main.py", "2", "3", "+"])
        code = main()
        assert code == 0
        captured = capsys.readouterr()
        assert "2 3 + = 5" in captured.out

    def test_main_module_run(self, monkeypatch):
        main_path = str(BASE_DIR / "main.py")
        monkeypatch.setattr(sys, "argv", ["main.py", "2", "3", "+"])
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(main_path, run_name="__main__")
        assert exc_info.value.code == 0
