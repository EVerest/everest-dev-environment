#!/bin/bash

# Initialize Node-RED flows with correct MQTT broker configuration
# This script runs before Node-RED starts to ensure proper configuration

echo "🔧 Initializing Node-RED flows..."

# Create Node-RED directory structure
mkdir -p /usr/src/node-red/.node-red

# Check if flows.json exists in /data
if [ -f /data/flows.json ]; then
    echo "📄 Found existing flows.json, copying to Node-RED directory..."

    # Replace localhost with mqtt-server in the flows.json file directly in /data
    sed -i 's/"broker": "localhost"/"broker": "mqtt-server"/g' /data/flows.json

    # Copy flows to Node-RED's expected location
    cp /data/flows.json /usr/src/node-red/.node-red/flows.json

    echo "✅ MQTT broker configuration updated to use mqtt-server:1883"
else
    echo "📄 No existing flows.json found, will use default configuration"
fi

echo "🔧 Node-RED flows initialization completed"