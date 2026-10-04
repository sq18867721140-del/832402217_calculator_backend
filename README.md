# StudentID_calculator_backend

前后端分离计算器系统的**后端**项目。负责表达式的解析、校验与计算，并把每次成功计算持久化到 SQLite 数据库。

> 请将目录名 `StudentID_calculator_backend` 中的 `StudentID` 替换为你的学号，例如 `20231234_calculator_backend`。

## 1. 技术栈

| 项目 | 选型 |
| --- | --- |
| 语言 | Python 3.10+（开发环境 3.11） |
| Web 框架 | FastAPI |
| ASGI 服务器 | Uvicorn |
| 数据校验 | Pydantic v2 |
| 数据库 | SQLite（Python 标准库 `sqlite3`） |
| 测试 | pytest + httpx |

**表达式计算完全在后端完成**，未使用 `eval` / `exec`。实现方式为：词法分析 → 调度场算法转后缀（RPN）→ 栈求值，全程使用 `decimal.Decimal` 保证小数精度。

## 2. 运行环境

- Python 3.10 及以上
- 无需额外安装数据库服务（SQLite 为文件数据库）
- 依赖见 `requirements.txt`

## 3. 安装方法

```bash
cd StudentID_calculator_backend

# 建议使用虚拟环境
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 4. 启动方法

```bash
# 在项目根目录执行
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

启动后：

- 服务地址：<http://127.0.0.1:8000>
- 交互式接口文档（Swagger UI）：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/api/health>

## 5. 配置说明

| 环境变量 | 说明 | 默认值 |
| --- | --- | --- |
| `DATABASE_PATH` | SQLite 数据库文件路径 | `<项目根>/data/calculator.db` |

例如：

```bash
# Windows PowerShell
$env:DATABASE_PATH = "D:\data\calculator.db"
uvicorn src.main:app --port 8000
```

## 6. 数据库初始化

数据库**无需手动初始化**。服务启动时（FastAPI lifespan）会自动创建 `data/` 目录、数据库文件以及 `calculation_history` 表。

表结构：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | 记录 ID |
| `expression` | TEXT NOT NULL | 计算表达式 |
| `result` | TEXT NOT NULL | 计算结果（字符串存储，保留精度） |
| `created_at` | TEXT NOT NULL | 计算时间，`YYYY-MM-DD HH:MM:SS` |

若需重新初始化，删除 `data/calculator.db` 后重启服务即可。

## 7. API 接口

| 方法 | 路径 | 说明 | 成功状态码 |
| --- | --- | --- | --- |
| POST | `/api/calculate` | 计算表达式并保存历史 | 200 |
| GET | `/api/history` | 获取全部历史（按 id 倒序） | 200 |
| DELETE | `/api/history/{id}` | 删除指定历史记录 | 200 |
| DELETE | `/api/history` | 清空全部历史（扩展功能） | 200 |
| GET | `/api/health` | 健康检查 | 200 |

### 请求 / 响应示例

计算：

```http
POST /api/calculate
Content-Type: application/json

{ "expression": "(1+2)*3" }
```

```json
{ "success": true, "id": 1, "expression": "(1+2)*3", "result": 9 }
```

错误（非法表达式 / 除零，HTTP 400）：

```json
{ "success": false, "message": "Division by zero" }
```

历史：

```json
[
  { "id": 1, "expression": "(1+2)*3", "result": 9, "created_at": "2026-10-04 23:11:40" }
]
```

命令行验证：

```bash
curl -X POST http://127.0.0.1:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d "{\"expression\":\"(1+2)*3\"}"

curl http://127.0.0.1:8000/api/history
```

## 8. 支持的计算能力

- 四则运算：`+ - * /`
- 运算符优先级与括号
- 一元正负号：`-5`、`3*-2`、`--5`
- 小数运算（`Decimal`，`0.1 + 0.2 = 0.3`）
- 非法表达式提示、除零提示
- 全角符号归一化：`× ÷ − （ ）`

## 9. 与前端连接方式

- 后端已开启 CORS（允许所有来源），前端可跨域调用。
- 前端在 `src/config.js` 中配置后端地址：

```js
window.APP_CONFIG = { API_BASE_URL: "http://127.0.0.1:8000" };
```

- 部署后把该地址改为公网后端地址即可，无需修改其他前端代码。

## 10. 运行测试

```bash
pytest -q
```

测试覆盖表达式解析（合法 / 非法 / 除零 / 精度）与完整 API 流程（计算 → 历史 → 删除 → 清空）。

## 11. 项目结构

```
StudentID_calculator_backend/
├── src/
│   ├── main.py                     # FastAPI 入口、CORS、异常处理
│   ├── calculator.py               # 表达式解析与计算（核心）
│   ├── database.py                 # SQLite 连接与建表
│   ├── controller/
│   │   ├── calculate_controller.py # POST /api/calculate
│   │   └── history_controller.py   # GET / DELETE /api/history
│   ├── service/
│   │   ├── calculator_service.py   # 计算编排
│   │   └── history_service.py      # 历史记录数据访问
│   └── model/
│       └── history.py              # Pydantic 请求/响应模型
├── tests/
│   ├── test_calculator.py
│   └── test_api.py
├── requirements.txt
├── codestyle.md
└── README.md
```

## 12. 部署提示

- 生产环境建议使用 `uvicorn src.main:app --host 0.0.0.0 --port $PORT`。
- 常见平台（Render / Railway / 云服务器）均可直接部署；注意保持服务在作业评估期间可访问。
- 部署到公网时，建议把 `main.py` 中的 `allow_origins=["*"]` 收紧为前端实际域名。
