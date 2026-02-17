.PHONY: add commit push clear-pycache clear-ruff clear-pytest clear build lint test 
IMAGE_NAME=retail-chat-agent-backend:latest

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
	$(IMAGE_NAME)

backend-start: backend-build backend-run

build:
	docker compose down -v || true
	docker compose up --build

clean:
	docker compose down -v || true
	docker system prune -af --volumes
	docker image prune -af
	docker volume prune -af