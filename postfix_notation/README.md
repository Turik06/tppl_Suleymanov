# Постфиксная стековая машина

## Запуск

```bash
python postfix_notation/main.py "3 0 4 ~ 2 ~"
```

Пример вывода:
```text
Шаг '3': [3]
Шаг '0': [3, 0]
Шаг '4': [3, 0, 4]
Шаг '~': [49]
Шаг '2': [49, 2]
Шаг '~': [47]
3 0 4 ~ 2 ~ = 47
```

## Тесты и покрытие

```bash
pytest postfix_notation/tests/
pytest --cov=postfix_notation.main --cov-report=term-missing postfix_notation/tests/
```
