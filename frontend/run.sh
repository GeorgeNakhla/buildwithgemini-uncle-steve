#!/usr/bin/env bash
set -e

# Load metadata if present
METADATA_FILE="$(dirname "$0")/../deployment_metadata.json"
if [ -f "$METADATA_FILE" ]; then
  export AGENT_ENGINE_RESOURCE_NAME="$(jq -r .remote_agent_runtime_id "$METADATA_FILE")"
  export AGENT_DIRECTORY="$(jq -r .agent_directory "$METADATA_FILE")"
fi

if [ -z "$AGENT_ENGINE_RESOURCE_NAME" ]; then
  export AGENT_ENGINE_RESOURCE_NAME="projects/323760082979/locations/us-central1/reasoningEngines/523721852443426816"
fi

if [ -z "$AGENT_DIRECTORY" ]; then
  export AGENT_DIRECTORY="app"
fi

PORT="${PORT:-8085}"
echo "Starting Uncle Steve Sportsbook Frontend..."
echo "  Resource: ${AGENT_ENGINE_RESOURCE_NAME}"
echo "  Directory: ${AGENT_DIRECTORY}"
echo "  URL: http://localhost:${PORT}"

exec python main.py
