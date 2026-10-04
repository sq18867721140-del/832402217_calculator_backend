"""Unit tests for the safe expression evaluator."""

from decimal import Decimal

import pytest

from src.calculator import ExpressionError, evaluate, format_result, to_number


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("12+8", "20"),
        ("1+2*3", "7"),
        ("(1+2)*3", "9"),
        ("10/2+7", "12"),
        ("8-3*2", "2"),
        ("-5+8", "3"),
        ("3*-2", "-6"),
        ("--5", "5"),
        ("0.1+0.2", "0.3"),
        ("2.5*4", "10"),
        ("((2+3)*(4-1))/5", "3"),
        ("1 + 2 × 3", "7"),
        ("9÷3", "3"),
        ("  7  ", "7"),
        ("0.5", "0.5"),
    ],
)
def test_evaluate_valid(expression, expected):
    assert format_result(evaluate(expression)) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "   ",
        "1+",
        "*2",
        "(1+2",
        "1+2)",
        "1+a",
        "1..2",
        "2(3)",
        "()",
        "1++",
    ],
)
def test_evaluate_invalid(expression):
    with pytest.raises(ExpressionError):
        evaluate(expression)


@pytest.mark.parametrize("expression", ["1/0", "5/(3-3)", "0/0"])
def test_division_by_zero(expression):
    with pytest.raises(ExpressionError, match="Division by zero"):
        evaluate(expression)


def test_precision_is_exact_for_decimals():
    # 0.1 + 0.2 must be exactly 0.3, not 0.30000000000000004.
    assert evaluate("0.1+0.2") == Decimal("0.3")


def test_repeating_decimal_is_rounded_for_display():
    assert format_result(evaluate("1/3")) == "0.333333333333"


def test_to_number_types():
    assert to_number(Decimal("9")) == 9
    assert isinstance(to_number(Decimal("9")), int)
    assert to_number(Decimal("2.5")) == 2.5
    assert isinstance(to_number(Decimal("2.5")), float)
