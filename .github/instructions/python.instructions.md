---
description: "Use when writing or refactoring Python backend code. Enforces modern Python 3.14+ typing and modern library choices (httpx, pendulum, polars, pydantic, etc)."
applyTo: "backend/**/*.py"
---

# Modern Python Backend Standards

- Target Python 3.14+ style in all new and modified code.
- Use builtin generic types and modern unions:
    - Use `list[str]`, `dict[str, int]`, `set[str]`, `tuple[int, ...]`
    - Use `A | B` instead of `Optional[A]` or `Union[A, B]`
- Do not import basic container/union types from `typing`:
    - Avoid `List`, `Dict`, `Set`, `Tuple`, `Optional`, `Union`
    - It is acceptable to use advanced typing features from `typing` when needed (for example `TypedDict`, `Protocol`, `Literal`, `Self`)
- Prefer modern libraries for new code unless project constraints require otherwise:
    - `httpx` over `requests`
    - `pendulum` over direct `datetime`-heavy logic for timezone-aware datetime operations
    - `polars` over `pandas`
    - `pydantic` for data validation and schema modeling
- Keep types explicit on public APIs (function params, returns, class attributes).
- Favor async I/O patterns in backend integrations when appropriate (for example `httpx.AsyncClient`).

## Example

```python
import httpx
import pendulum
from pydantic import BaseModel

class Quote(BaseModel):
    id: str
    created_at: pendulum.DateTime


async def fetch_quote_ids(client: httpx.AsyncClient) -> list[str]:
    response = await client.get("https://example.com/quotes")
    response.raise_for_status()
    payload: list[dict[str, str]] = response.json()
    return [row["id"] for row in payload]
```
