# 832402217_calculator_backend

The **backend** of a front-end / back-end separated calculator system. It handles expression parsing, validation and calculation, and persists every successful calculation to a SQLite database.

## 1. Tech Stack

| Item | Choice |
| --- | --- |
| Language | Python 3.10+ (developed on 3.11) |
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| Validation | Pydantic v2 |
| Database | SQLite (Python standard library `sqlite3`) |
| Testing | pytest + httpx |

**All expression calculation happens on the back end**, with no `eval` / `exec`. Implementation: lexical analysis → shunting-yard algorithm to Reverse Polish Notation (RPN) → stack evaluation, using `decimal.Decimal` throughout to guarantee decimal precision.

## 2. Runtime Environment

- Python 3.10 or higher
- No separate database service required (SQLite is a file-based database)
- Dependencies listed in `requirements.txt`

## 3. Installation

```bash
cd 832402217_calculator_backend

# A virtual environment is recommended
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 4. Running

```bash
# From the project root
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

After startup:

- Service address: <http://127.0.0.1:8000>
- Interactive API docs (Swagger UI): <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/api/health>

## 5. Configuration

| Environment variable | Description | Default |
| --- | --- | --- |
| `DATABASE_PATH` | Path of the SQLite database file | `<project root>/data/calculator.db` |

Example:

```bash
# Windows PowerShell
$env:DATABASE_PATH = "D:\data\calculator.db"
uvicorn src.main:app --port 8000
```

## 6. Database Initialization

The database **requires no manual initialization**. On service startup (FastAPI lifespan), the `data/` directory, the database file and the `calculation_history` table are created automatically.

Table structure:

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Record ID |
| `expression` | TEXT NOT NULL | The calculation expression |
| `result` | TEXT NOT NULL | The result (stored as text to preserve precision) |
| `created_at` | TEXT NOT NULL | Calculation time, `YYYY-MM-DD HH:MM:SS` |

To reinitialize, delete `data/calculator.db` and restart the service.

## 7. API

| Method | Path | Description | Success status code |
| --- | --- | --- | --- |
| POST | `/api/calculate` | Evaluate an expression and save it to history | 200 |
| GET | `/api/history` | Get all history (id descending) | 200 |
| DELETE | `/api/history/{id}` | Delete one history record | 200 |
| DELETE | `/api/history` | Clear all history (extension) | 200 |
| GET | `/api/health` | Health check | 200 |

### Request / Response examples

Calculate:

```http
POST /api/calculate
Content-Type: application/json

{ "expression": "(1+2)*3" }
```

```json
{ "success": true, "id": 1, "expression": "(1+2)*3", "result": 9 }
```

Error (invalid expression / division by zero, HTTP 400):

```json
{ "success": false, "message": "Division by zero" }
```

History:

```json
[
  { "id": 1, "expression": "(1+2)*3", "result": 9, "created_at": "2026-10-04 23:11:40" }
]
```

Command-line verification:

```bash
curl -X POST http://127.0.0.1:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d "{\"expression\":\"(1+2)*3\"}"

curl http://127.0.0.1:8000/api/history
```

## 8. Supported Capabilities

- Four basic operations: `+ - * /`
- Operator precedence and parentheses
- Unary plus / minus: `-5`, `3*-2`, `--5`
- Decimal arithmetic (`Decimal`, `0.1 + 0.2 = 0.3`)
- Invalid-expression and division-by-zero messages
- Full-width symbol normalization: `× ÷ − （ ）`

## 9. Connecting to the Front End

- CORS is enabled (all origins allowed) so the front end can call the API cross-origin.
- The front end configures the backend address in `src/config.js`:

```js
window.APP_CONFIG = { API_BASE_URL: "http://127.0.0.1:8000" };
```

- After deployment, change that address to the public backend URL; no other front-end code needs to change.

## 10. Running Tests

```bash
pytest -q
```

Tests cover expression parsing (valid / invalid / division by zero / precision) and the full API flow (calculate → history → delete → clear).

## 11. Project Structure

```
832402217_calculator_backend/
├── src/
│   ├── main.py                     # FastAPI entry point, CORS, exception handlers
│   ├── calculator.py               # Expression parsing and calculation (core)
│   ├── database.py                 # SQLite connection and schema
│   ├── controller/
│   │   ├── calculate_controller.py # POST /api/calculate
│   │   └── history_controller.py   # GET / DELETE /api/history
│   ├── service/
│   │   ├── calculator_service.py   # Calculation orchestration
│   │   └── history_service.py      # History data access
│   └── model/
│       └── history.py              # Pydantic request/response models
├── tests/
│   ├── test_calculator.py
│   └── test_api.py
├── requirements.txt
├── codestyle.md
└── README.md
```

## 12. Deployment Notes

- For production, run `uvicorn src.main:app --host 0.0.0.0 --port $PORT`.
- Common platforms (Render / Railway / a cloud server) can deploy directly; keep the service accessible during the grading period.
- When deploying publicly, consider tightening `allow_origins=["*"]` in `main.py` to the front end's actual domain.
