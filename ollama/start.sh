#!/bin/sh
MODEL_NAME="llama3.1:8B"
EMBEDDING_NAME="llama3"

ollama serve &
sleep 10
ollama pull $MODEL_NAME
ollama pull $EMBEDDING_NAME
tail -f /dev/null
