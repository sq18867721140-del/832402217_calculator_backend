# Backend Code Style

## 代码规范来源

本项目后端代码遵循 **[PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)**，
并参考 **[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)** 中的注释与文档字符串约定。

- PEP 8：<https://peps.python.org/pep-0008/>
- Google Python Style Guide：<https://google.github.io/styleguide/pyguide.html>

## 1. 命名规范

| 元素 | 规则 | 示例 |
| --- | --- | --- |
| 模块 / 包 | 小写 + 下划线 | `history_service.py` |
| 类 / 异常 | 大驼峰 `PascalCase` | `ExpressionError`、`CalculateRequest` |
| 函数 / 方法 / 变量 | 小写 + 下划线 `snake_case` | `evaluate()`、`record_id` |
| 常量 | 全大写 + 下划线 | `MAX_DECIMAL_PLACES`、`_PRECEDENCE` |
| 模块内部私有 | 前缀单下划线 | `_tokenize()`、`_eval_rpn()` |

## 2. 缩进与格式

- 使用 **4 个空格** 缩进，禁止 Tab。
- 每行不超过 **88** 个字符（与 Black 默认一致）。
- 顶层定义之间空 **2 行**，类内方法之间空 **1 行**。
- 运算符两侧、逗号 / 冒号后各保留一个空格。
- 文件统一使用 **UTF-8** 编码，字符串优先使用双引号以与格式化工具保持一致。

## 3. 导入规范

- 所有导入置于文件顶部。
- 顺序：标准库 → 第三方库 → 本项目模块，各组之间用空行分隔。
- 优先使用绝对导入；包内部使用显式相对导入（如 `from ..calculator import evaluate`）。
- 禁止使用 `from module import *`。

## 4. 类型注解

- 所有公开函数、方法必须标注参数与返回值类型。
- 使用 `from __future__ import annotations` 以便使用前向引用。
- 复杂类型使用 `typing`（`List`、`Dict`、`Optional` 等）。

```python
def evaluate(expression: str) -> Decimal:
    ...
```

## 5. 文档字符串

- 所有公开模块、类、函数使用文档字符串。
- 使用三重双引号；一行可写完时保持单行。

```python
def delete_one(record_id: int) -> int:
    """Delete a single record, returning the number of deleted rows."""
```

## 6. 错误处理

- 业务异常使用自定义异常类（`ExpressionError`），不抛裸 `Exception`。
- 禁止空 `except:`；捕获异常时明确异常类型。
- 资源的获取与释放使用上下文管理器（`with`）或 `try/finally`，保证连接关闭。
- **严禁使用 `eval` / `exec` 执行用户输入。**

## 7. 注释

- 注释用于解释「为什么」，而非「做什么」。
- 注释与代码同步更新，避免失效注释。
- 行内注释与代码至少间隔 2 个空格。

## 8. 分层约定

- `controller` 仅处理 HTTP 请求 / 响应与状态码。
- `service` 承载业务编排。
- `model` 只放数据模型。
- 数据库访问集中管理，不在 controller 中直接拼 SQL。

## 9. 检查工具（可选）

```bash
pip install flake8 black isort
black .
isort .
flake8 src tests
```
