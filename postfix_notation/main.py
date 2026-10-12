import math
from typing import List, Union

Number = Union[int, float]


class CaringStackMachineError(Exception):
    pass


def to_int_if_whole(value: Number) -> Number:
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def format_num(value: Number) -> str:
    value = to_int_if_whole(value)
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def validate_number(value: Number) -> None:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise CaringStackMachineError("Обнаружено некорректное значение (NaN или бесконечность).")


def parse_number(token: str) -> Union[Number, None]:
    if token.lower() in {"nan", "inf", "-inf", "+inf"}:
        raise CaringStackMachineError(f"Специальное значение '{token}' не поддерживается.")
    try:
        return int(token)
    except ValueError:
        try:
            val = float(token)
            validate_number(val)
            return to_int_if_whole(val)
        except ValueError:
            return None


def evaluate_postfix(expression: str, verbose: bool = True) -> Number:
    tokens = expression.strip().split()
    if not tokens:
        raise CaringStackMachineError("Выражение не должно быть пустым.")

    stack: List[Number] = []

    for token in tokens:
        num = parse_number(token)

        if num is not None:
            stack.append(num)

        elif token in {"+", "-", "*", "/"}:
            if len(stack) < 2:
                raise CaringStackMachineError(f"Для операции '{token}' нужно минимум 2 операнда в стеке.")
            b = stack.pop()
            a = stack.pop()

            try:
                if token == "+":
                    res = a + b
                elif token == "-":
                    res = a - b
                elif token == "*":
                    res = a * b
                elif token == "/":
                    if b == 0:
                        raise CaringStackMachineError("Деление на ноль невозможно. Пожалуйста, проверьте выражение.")
                    res = a / b
            except OverflowError:
                raise CaringStackMachineError("Произошло арифметическое переполнение. Числа слишком велики.")

            validate_number(res)
            stack.append(to_int_if_whole(res))

        elif token == "~":
            if len(stack) < 2:
                raise CaringStackMachineError("Для операции '~' нужно минимум 2 операнда в стеке.")
            y = stack[-1]
            x = stack[-2]

            try:
                if x != 0 and y != 0:
                    stack.pop()
                    stack.pop()
                    res = abs(x - y)
                else:
                    res = sum(stack) ** 2
                    stack.clear()
            except OverflowError:
                raise CaringStackMachineError("Произошло переполнение при вычислении операции '~'.")

            validate_number(res)
            stack.append(to_int_if_whole(res))

        else:
            raise CaringStackMachineError(f"Неизвестный токен '{token}'.")

        if verbose:
            stack_repr = "[" + ", ".join(format_num(val) for val in stack) + "]"
            print(f"Шаг '{token}': {stack_repr}")

    if len(stack) != 1:
        raise CaringStackMachineError(
            f"В стеке осталось {len(stack)} чисел вместо одного. Проверьте выражение."
        )

    return stack[0]
