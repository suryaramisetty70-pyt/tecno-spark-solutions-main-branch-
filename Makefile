.PHONY: help setup dev test lint clean docker-up docker-down

help:
	@echo "Buddy AI OS - Development Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Install all dependencies"
	@echo "  make install-pip    - Install Python dependencies"
	@echo "  make install-npm    - Install Node dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start development environment"
	@echo "  make backend        - Start backend only"
	@echo "  make frontend       - Start frontend only"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run linting and formatting"
	@echo "  make format         - Format code automatically"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      - Start Docker services"
	@echo "  make docker-down    - Stop Docker services"
	@echo "  make docker-logs    - Show Docker service logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Remove build artifacts"
	@echo "  make reset          - Reset development environment"
	@echo ""

setup:
	bash scripts/setup-dev.sh

install-pip:
	cd backend && pip install -r requirements-dev.txt

install-npm:
	cd frontend-web && npm install --legacy-peer-deps

dev:
	bash scripts/dev.sh

backend:
	cd backend && source venv/bin/activate && uvicorn api.main:app --reload

frontend:
	cd frontend-web && npm run dev

test:
	cd backend && python -m pytest tests/ -v --cov=core --cov=agents

lint:
	cd backend && flake8 . && pylint **/*.py

format:
	cd backend && black . && isort .
	cd frontend-web && npm run format

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/build backend/dist backend/.eggs *.egg-info
	rm -rf frontend-web/dist frontend-web/node_modules
	rm -rf .coverage htmlcov

reset: clean
	rm -rf backend/venv
	rm -rf frontend-web/node_modules
	make setup

.DEFAULT_GOAL := help
