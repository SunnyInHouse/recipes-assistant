"""
Проверяет, что значение value равно либо 0, либо 1.
"""

from decimal import Decimal


def check_value_is_0_or_1(value: Decimal) -> bool:

    return value in (0, 1)
