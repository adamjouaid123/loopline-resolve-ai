# Contributing

This is a solo AI-103 capstone project, built in phases documented in `LoopLine-Resolve-AI-AI103-Capstone-Guide.md`. Contributions from others aren't expected, but if you're picking this up:

1. Create a virtual environment and install dev dependencies: `uv pip install -e ".[dev]"`.
2. Run tests before committing: `pytest -q`.
3. Lint/type-check: `ruff check .` and `mypy app`.
4. Keep provider implementations (Azure/local/mock) behind the shared protocols in `app/providers/protocols.py` — the application layer should never import a specific provider's SDK directly.
5. Never commit `.env`, API keys, or real personal data. All sample data must stay synthetic.
6. Follow the phase order in the capstone guide (Section 19) — later phases assume earlier ones are in place.
