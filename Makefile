.PHONY: add commit push clear-pycache clear-ruff clear-pytest clear build-ollama run-ollama lint test 

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

build-ollama:
	cd ollama
	docker build -t custom-ollama:latest .

run-ollama: build-ollama
	docker run -d --name custom-ollama-container -p 11434:11434 -v ollama_data:/root/.ollama custom-ollama:latest

lint:
	python3 -m ruff format .
	python3 -m ruff check .

test:
	python3 -m pytest -vv tests/