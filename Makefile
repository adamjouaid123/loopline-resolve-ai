.PHONY: install test lint api web web-install web-build ui clean

install:
	uv pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check .
	mypy app

# Backend API (serves the React UI's data). Run this in one terminal…
api:
	uvicorn app.api.main:app --reload

# …and the React dev server in another (proxies /api to the backend on :8000).
web-install:
	cd web && npm install

web:
	cd web && npm run dev

web-build:
	cd web && npm run build

# Legacy Streamlit shell (kept from Phase 1; the React app in web/ is primary).
ui:
	streamlit run ui/streamlit_app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache
