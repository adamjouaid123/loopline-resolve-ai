.PHONY: install test lint run ui clean

install:
	uv pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check .
	mypy app

run:
	uvicorn app.api.main:app --reload

ui:
	streamlit run ui/streamlit_app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache
