.PHONY: add commit push clear-pycache clear-ruff clear-pytest clear lint test build up down restart logs clean

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Available targets:"
	@echo "  add                 Stage all changes for commit"
	@echo "  commit              Commit staged changes with a message"
	@echo "  push                Push committed changes to remote repository"
	@echo "  clear               Clear Python cache, ruff cache, and pytest cache"
	@echo "  lint                Run ruff to format and check code"
	@echo "  test                Run pytest on the tests/ directory"
	@echo "  build               Build all service images via Docker Compose"
	@echo "  up                  Start all services in detached mode"
	@echo "  down                Stop and remove all containers"
	@echo "  restart             Restart all services"
	@echo "  logs                Tail logs for all services"
	@echo "  clean               Stop containers and remove images and volumes"
	@echo ""

add:
	git add .

commit: add
	git commit -m "$(msg)"

push: commit
	git push

new-branch:
	git switch -c $(branch_name)

clear-pycache:
	find . -type d -name '__pycache__' -exec rm -rf {} +

clear-ruff: clear-pycache
	find . -type d -name '.ruff_cache' -exec rm -rf {} +

clear-pytest: clear-ruff
	find . -type d -name '.pytest_cache' -exec rm -rf {} +

clear: clear-pytest
	clear

lint:
	python3 -m ruff format .
	python3 -m ruff check .

test:
	python3 -m pytest -vv tests/

build:
	docker compose build
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

clean:
	docker compose down -v --rmi all
