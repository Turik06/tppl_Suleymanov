import math
import sys

HELP_MESSAGE = """Стековая машина для вычисления выражений в постфиксной нотации (RPN).

Использование:
    python main.py "<выражение>"
    python main.py -h | --help

Поддерживаемые операции:
    +   сложение (x + y)
    -   вычитание (x - y)
    *   умножение (x * y)
    /   деление (x / y)
    ~   специальный оператор:
        - если x != 0 и y != 0: вычисляет |x - y| и кладет результат в стек
        - если x == 0 или y == 0: вычисляет сумму всех значений в стеке,
          включая извлеченные операнды, возводит её в квадрат и кладет результат обратно в стек

Примеры:
    python main.py "3 0 4 ~ 2 ~"
    python main.py "2 2 + 4 - 4 ~ 2 3 * +"
"""


def is_numeric(token: str) -> bool:
    try:
        return math.isfinite(float(token))
    except ValueError:
        return False


def to_int_if_whole(val: int | float) -> int | float:
    if isinstance(val, float) and val.is_integer():
        return int(val)
    return val


def parse_token(token: str) -> int | float:
    return to_int_if_whole(float(token))


def calc_sum(x: int | float, y: int | float) -> int | float:
    return to_int_if_whole(x + y)


def calc_sub(x: int | float, y: int | float) -> int | float:
    return to_int_if_whole(x - y)


def calc_mul(x: int | float, y: int | float) -> int | float:
    return to_int_if_whole(x * y)


def calc_div(x: int | float, y: int | float) -> int | float:
    if y == 0:
        raise ZeroDivisionError("Деление на ноль невозможно.")
    return to_int_if_whole(x / y)


def calc_tilde(stack: list[int | float]) -> list[int | float]:
    if len(stack) < 2:
        raise ValueError("Операция '~' требует не менее двух операндов.")
    y = stack.pop()
    x = stack.pop()

    if x == 0 or y == 0:
        total = sum(stack) + x + y
        stack.clear()
        stack.append(to_int_if_whole(total ** 2))
    else:
        stack.append(to_int_if_whole(abs(x - y)))

    return stack


BINARY_OPERATIONS = {
    "+": calc_sum,
    "-": calc_sub,
    "*": calc_mul,
    "/": calc_div,
}


def format_result(val: int | float) -> str:
    return str(to_int_if_whole(val))


def evaluate_expression(expression: str, verbose: bool = True) -> int | float:
    tokens = expression.strip().split()
    if not tokens:
        raise ValueError("Выражение не должно быть пустым.")

    stack: list[int | float] = []

    for step, token in enumerate(tokens, start=1):
        match token:
            case "+" | "-" | "*" | "/":
                if len(stack) < 2:
                    raise ValueError(f"Операция '{token}' требует не менее двух операндов.")
                right = stack.pop()
                left = stack.pop()
                stack.append(BINARY_OPERATIONS[token](left, right))

            case "~":
                calc_tilde(stack)

            case _ if is_numeric(token):
                stack.append(parse_token(token))

            case _ if "/" in token:
                raise ValueError(
                    f"Токен '{token}' похож на путь. Оберните выражение в кавычки, чтобы '~' не раскрывался."
                )

            case _:
                raise ValueError(f"Неизвестный токен в выражении: '{token}'")

        if verbose:
            print(f"Шаг {step:2d}: токен '{token}' -> стек: {stack}")

    if len(stack) != 1:
        raise ValueError(
            f"В стеке после вычислений должно остаться ровно одно число, осталось: {stack}"
        )

    return stack[0]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if not args:
        print("Использование: python main.py \"<постфиксное выражение>\"")
        print("Пример: python main.py \"3 0 4 ~ 2 ~\"")
        print("Справка: python main.py --help")
        return 1

    if args[0] in ("-h", "--help"):
        print(HELP_MESSAGE.strip())
        return 0

    raw_expression = " ".join(args)
    try:
        result = evaluate_expression(raw_expression, verbose=True)
        print(f"\n{raw_expression} = {format_result(result)}")
        return 0
    except Exception as err:
        print(f"Ошибка вычисления: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
