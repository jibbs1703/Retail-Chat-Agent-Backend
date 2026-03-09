.PHONY: add commit push clear-pycache clear-ruff clear-pytest clear lint test  backend-build backend-run backend-start backend-stop backend-restart backend-clean

IMAGE_NAME=retail-chat-agent-backend:latest
CONTAINER_NAME=retail-chat-agent-backend-container

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
	@echo "  backend-build       Build the backend Docker image"
	@echo "  backend-run         Run the backend Docker container"
	@echo "  backend-start       Build and run the backend Docker container"
	@echo "  backend-stop        Stop and remove the backend Docker container"
	@echo "  backend-restart     Restart the backend Docker container"
	@echo "  backend-clean       Clean up Docker images, containers, and volumes"
	@echo ""

add:
	git add .

commit: add
	git commit -m "$(msg)"

push: commit
	git push

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

backend-build:
	docker build -f backend/Dockerfile -t $(IMAGE_NAME) .

backend-run:
	docker run \
	-p 8000:8000 \
	-v $(shell pwd)/backend/app:/app/app \
	--name $(CONTAINER_NAME) \
	$(IMAGE_NAME)

backend-start: backend-build backend-run

backend-stop:
	@docker stop $(CONTAINER_NAME) || true
	@docker rm $(CONTAINER_NAME) || true

backend-restart: backend-stop backend-start

backend-clean: backend-stop
	@docker system prune -af --volumes
	@docker image prune -af
	@docker volume prune -af