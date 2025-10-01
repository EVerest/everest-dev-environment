#!/bin/bash

# Initialize Node-RED with default welcome flow
echo "🌐 Initializing Node-RED with default welcome flow..."

# Docker Compose project name (defaults to current folder name with _devcontainer suffix, can be overridden)
# This matches VSC's naming convention: {workspace-folder-name}_devcontainer-{service-name}-1
DOCKER_COMPOSE_PROJECT_NAME="${DOCKER_COMPOSE_PROJECT_NAME:-$(basename "$(pwd)")_devcontainer}"

# Function to run docker compose with project name
docker_compose() {
    docker compose -p "$DOCKER_COMPOSE_PROJECT_NAME" -f .devcontainer/docker-compose.yml -f .devcontainer/general-devcontainer/docker-compose.devcontainer.yml "$@"
}

# Check if Node-RED container is running
if ! docker_compose ps | grep -q "nodered"; then
    echo "❌ Error: Node-RED container is not running"
    echo "💡 Please start with './setup start' first"
    exit 1
fi

# Copy default flow to Node-RED volume
echo "📄 Copying default welcome flow..."
docker cp .devcontainer/default-nodered-flow.json ${DOCKER_COMPOSE_PROJECT_NAME}-nodered-1:/data/flows.json

# Restart Node-RED to load the default flow
echo "🔄 Restarting Node-RED to load default flow..."
docker_compose restart nodered

# Clean up temporary file
rm -f /tmp/flows.json

echo "✅ Node-RED initialized with default welcome flow!"
echo "🌐 Access at: http://localhost:1881/ui"