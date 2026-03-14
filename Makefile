PYTHON ?= python3

.PHONY: setup api serve cli seed test frontend

setup:
	cd backend && $(PYTHON) -m pip install -e .[dev]

api:
	cd backend && uvicorn opencost.api.main:app --reload --host 127.0.0.1 --port 4680

serve:
	cd backend && opencost serve --host 127.0.0.1 --port 4680

cli:
	cd backend && opencost --help

seed:
	cd backend && opencost seed

test:
	cd backend && pytest -q

frontend:
	cd frontend && npm install && npm run dev
