#!/bin/bash
set -e

CONTAINER_NAME="dopi-container"

if [[ ! -f .env ]]; then
    echo ".env file not found."
    exit 1
fi

if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "Removing existing container: $CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME"
fi

docker build -t dopi .
source .env
docker run --env-file .env -p 8888:"$PORT" --name "$CONTAINER_NAME" -it dopi
