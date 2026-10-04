"""Safe arithmetic expression evaluator.

This module implements the *whole* calculation logic of the project on the
back end.  It never uses ``eval`` / ``exec`` or any other mechanism that
executes user input as program code.  Instead it:

1. tokenizes the raw expression,
2. converts the token stream into Reverse Polish Notation (RPN) with the
   shunting-yard algorithm,
3. evaluates the RPN with an explicit stack.

Supported features
------------------
* binary operators ``+ - * /`` (``×`` / ``÷`` are normalized to ``*`` / ``/``)
* operator precedence and parentheses
* unary plus / minus (``-5``, ``3 * -2``, ``--5``)
* decimal numbers
* clear errors for invalid expressions and division by zero
"""

from __future__ import annotations

from decimal import (
    Decimal,
    DivisionByZero,
    InvalidOperation,
    ROUND_HALF_UP,
    getcontext,
)
from typing import List, Tuple

# 28 significant digits is plenty for a calculator while keeping Decimal fast.
getcontext().prec = 28

# Non-terminating results (e.g. 1 / 3) are rounded to this many decimals.
MAX_DECIMAL_PLACES = 12

# Guard against pathological input.
MAX_EXPRESSION_LENGTH = 1000

# Characters users may type that mean the same as ASCII operators.
_CHAR_MAP = {
    "×": "*",
    "✕": "*",
    "÷": "/",
    "−": "-",
    "－": "-",
    "＋": "+",
    "（": "(",
    "）": ")",
}

_PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "u+": 3, "u-": 3}
_RIGHT_ASSOCIATIVE = {"u+", "u-"}

# token = ("num", Decimal) | ("op", str) | ("unary", str)
#       | ("lparen", "(") | ("rparen", ")")
Token = Tuple[str, object]


class ExpressionError(ValueError):
    """Raised when an expression is empty, malformed, or cannot be computed."""


def _tokenize(expression: str) -> List[Token]:
    tokens: List[Token] = []
    length = len(expression)
    index = 0
    prev = None  # kind of the previous token, used to detect unary +/-.

    while index < length:
        raw = expression[index]

        if raw.isspace():
            index += 1
            continue

        char = _CHAR_MAP.get(raw, raw)

        # --- numbers -----------------------------------------------------
        if char.isdigit() or char == ".":
            start = index
            dots = 0
            while index < length and (expression[index].isdigit() or expression[index] == "."):
                if expression[index] == ".":
                    dots += 1
                index += 1
            number_text = expression[start:index]
            if dots > 1:
                raise ExpressionError(f"Invalid number: '{number_text}'")
            try:
                value = Decimal(number_text)
            except InvalidOperation:
                raise ExpressionError(f"Invalid number: '{number_text}'")
            tokens.append(("num", value))
            prev = "num"
            continue

        # --- plus / minus (unary or binary) ------------------------------
        if char in "+-":
            if prev in (None, "op", "unary", "lparen"):
                tokens.append(("unary", char))
                prev = "unary"
            else:
                tokens.append(("op", char))
                prev = "op"
            index += 1
            continue

        # --- multiplication / division -----------------------------------
        if char in "*/":
            if prev in (None, "op", "unary", "lparen"):
                raise ExpressionError(f"Unexpected operator '{char}'")
            tokens.append(("op", char))
            prev = "op"
            index += 1
            continue

        # --- parentheses --------------------------------------------------
        if char == "(":
            if prev in ("num", "rparen"):
                raise ExpressionError("Missing operator before '('")
            tokens.append(("lparen", "("))
            prev = "lparen"
            index += 1
            continue

        if char == ")":
            if prev in (None, "op", "unary", "lparen"):
                raise ExpressionError("Unexpected ')'")
            tokens.append(("rparen", ")"))
            prev = "rparen"
            index += 1
            continue

        raise ExpressionError(f"Invalid character: '{raw}'")

    return tokens


def _should_pop(top_operator: str, current_operator: str) -> bool:
    """Decide whether *top_operator* can be emitted before *current_operator*.

    Higher precedence always pops. On equal precedence, left-associative
    operators pop (binary ``+ - * /``), while right-associative ones do not
    (unary ``u+ u-``), which keeps ``--5`` correct.
    """
    top_precedence = _PRECEDENCE[top_operator]
    current_precedence = _PRECEDENCE[current_operator]
    if top_precedence > current_precedence:
        return True
    if top_precedence == current_precedence and current_operator not in _RIGHT_ASSOCIATIVE:
        return True
    return False


def _to_rpn(tokens: List[Token]) -> List[Token]:
    output: List[Token] = []
    stack: List[str] = []

    for kind, value in tokens:
        if kind == "num":
            output.append((kind, value))
        elif kind == "unary":
            operator = "u" + str(value)
            while stack and stack[-1] in _PRECEDENCE and _should_pop(stack[-1], operator):
                output.append(("op", stack.pop()))
            stack.append(operator)
        elif kind == "op":
            operator = str(value)
            while stack and stack[-1] in _PRECEDENCE and _should_pop(stack[-1], operator):
                output.append(("op", stack.pop()))
            stack.append(operator)
        elif kind == "lparen":
            stack.append("(")
        elif kind == "rparen":
            while stack and stack[-1] != "(":
                output.append(("op", stack.pop()))
            if not stack:
                raise ExpressionError("Mismatched parentheses")
            stack.pop()  # discard the matching '('

    while stack:
        top = stack.pop()
        if top == "(":
            raise ExpressionError("Mismatched parentheses")
        output.append(("op", top))

    return output


def _eval_rpn(rpn: List[Token]) -> Decimal:
    stack: List[Decimal] = []

    for kind, value in rpn:
        if kind == "num":
            stack.append(value)  # type: ignore[arg-type]
            continue

        operator = str(value)
        if operator in ("u+", "u-"):
            if not stack:
                raise ExpressionError("Invalid expression")
            operand = stack.pop()
            stack.append(operand if operator == "u+" else -operand)
            continue

        if len(stack) < 2:
            raise ExpressionError("Invalid expression")
        right = stack.pop()
        left = stack.pop()

        if operator == "+":
            stack.append(left + right)
        elif operator == "-":
            stack.append(left - right)
        elif operator == "*":
            stack.append(left * right)
        elif operator == "/":
            if right == 0:
                raise ExpressionError("Division by zero")
            try:
                stack.append(left / right)
            except (DivisionByZero, InvalidOperation):
                raise ExpressionError("Division by zero")
        else:  # pragma: no cover - defensive, should never happen
            raise ExpressionError(f"Unknown operator '{operator}'")

    if len(stack) != 1:
        raise ExpressionError("Invalid expression")

    result = stack[0]
    if not result.is_finite():
        raise ExpressionError("Result is not a finite number")
    return result


def evaluate(expression: str) -> Decimal:
    """Evaluate *expression* and return the exact Decimal result.

    Raises :class:`ExpressionError` for any invalid input.
    """
    if expression is None or not str(expression).strip():
        raise ExpressionError("Expression is empty")

    text = str(expression).strip()
    if len(text) > MAX_EXPRESSION_LENGTH:
        raise ExpressionError("Expression is too long")

    tokens = _tokenize(text)
    if not tokens:
        raise ExpressionError("Expression is empty")

    rpn = _to_rpn(tokens)
    return _eval_rpn(rpn)


def format_result(value: Decimal) -> str:
    """Format a Decimal for human-readable storage and display."""
    result = value
    exponent = result.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -MAX_DECIMAL_PLACES:
        try:
            result = result.quantize(
                Decimal(1).scaleb(-MAX_DECIMAL_PLACES), rounding=ROUND_HALF_UP
            )
        except InvalidOperation:  # pragma: no cover - extremely large numbers
            pass

    result = result.normalize()
    text = format(result, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in ("", "-", "-0"):
        text = "0"
    return text


def to_number(value: Decimal):
    """Convert a Decimal to a JSON-friendly int/float."""
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def to_number_from_text(text: str):
    """Convert a stored result string back to a JSON-friendly int/float."""
    try:
        return to_number(Decimal(text))
    except InvalidOperation:
        return text
