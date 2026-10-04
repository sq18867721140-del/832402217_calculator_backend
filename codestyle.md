# Backend Code Style

## Source of the Standard

This project's backend code follows **[PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)**, and references the **[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)** for its commenting and docstring conventions.

- PEP 8: <https://peps.python.org/pep-0008/>
- Google Python Style Guide: <https://google.github.io/styleguide/pyguide.html>

## 1. Naming

| Element | Rule | Example |
| --- | --- | --- |
| Module / package | lowercase with underscores | `history_service.py` |
| Class / exception | `PascalCase` | `ExpressionError`, `CalculateRequest` |
| Function / method / variable | lowercase with underscores `snake_case` | `evaluate()`, `record_id` |
| Constant | uppercase with underscores | `MAX_DECIMAL_PLACES`, `_PRECEDENCE` |
| Module-private member | single leading underscore | `_tokenize()`, `_eval_rpn()` |

## 2. Indentation and Formatting

- Use **4 spaces** for indentation; tabs are forbidden.
- Keep lines under **88** characters (matching the Black default).
- Leave **2 blank lines** between top-level definitions and **1 blank line** between methods in a class.
- Keep a single space on both sides of operators and after commas / colons.
- Files are **UTF-8** encoded; prefer double quotes for strings to stay consistent with the formatter.

## 3. Imports

- Put all imports at the top of the file.
- Order them: standard library → third-party → project modules, with a blank line between groups.
- Prefer absolute imports; use explicit relative imports inside a package (e.g. `from ..calculator import evaluate`).
- Never use `from module import *`.

## 4. Type Annotations

- All public functions and methods must annotate parameter and return types.
- Use `from __future__ import annotations` to enable forward references.
- Use `typing` for complex types (`List`, `Dict`, `Optional`, etc.).

```python
def evaluate(expression: str) -> Decimal:
    ...
```

## 5. Docstrings

- All public modules, classes and functions have docstrings.
- Use triple double quotes; keep a one-line docstring when it fits.

```python
def delete_one(record_id: int) -> int:
    """Delete a single record, returning the number of deleted rows."""
```

## 6. Error Handling

- Use custom exception classes for business errors (e.g. `ExpressionError`), never bare `Exception`.
- No bare `except:`; always catch explicit exception types.
- Acquire and release resources with context managers (`with`) or `try/finally` to guarantee connections are closed.
- **Never use `eval` / `exec` to execute user input.**

## 7. Comments

- Comments explain "why", not "what".
- Keep comments in sync with the code; remove stale comments.
- Leave at least 2 spaces between inline comments and code.

## 8. Layering Conventions

- `controller` only handles HTTP requests / responses and status codes.
- `service` carries the business orchestration.
- `model` contains data models only.
- Database access is centralized; never build raw SQL in controllers.

## 9. Check Tools (optional)

```bash
pip install flake8 black isort
black .
isort .
flake8 src tests
```
