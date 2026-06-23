---
paths:
  - "**/*.py"
---

# Python Style Rules

- Type hints required on all public functions and methods
- Use f-strings over `.format()` or `%` formatting
- Use `dataclasses` or Pydantic for structured data, not plain dicts
- Follow PEP 8: 4-space indent, 88-char line limit (Black-compatible)
- Use `pathlib.Path` over `os.path` for file operations
- Never use bare `except:` -- always name the exception type
- Prefer `logging` over `print` for diagnostic output
