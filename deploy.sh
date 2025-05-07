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

# source .env file vars
export $(grep -v '^#' .env | xargs)

docker build -t dopi .
docker run --env-file .env -p "$HOST_PORT":"$PORT" --name "$CONTAINER_NAME" dopi
