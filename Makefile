.PHONY: add commit push clear-pycache clear-ruff clear-pytest clear build lint test 

add:
	git add .

build:
	docker compose down -v || true
	docker compose up --build

clean:
	docker compose down -v || true
	docker system prune -af --volumes
	docker image prune -af
	docker volume prune -af

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