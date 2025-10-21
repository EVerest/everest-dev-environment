# EVerest SIL Simulation Guide

This guide explains how to set up and run Software-In-the-Loop (SIL) simulations in the development environment.

## Overview

EVerest provides a complete development environment simulations with:

- **Node-RED UI**: Web-based interface for monitoring and control
- **SIL Configurations**: Pre-configured simulation scenarios
- **Build Scripts**: Automated setup and execution
- **Development Tools**: MQTT Explorer, Steve, and more

## 🎯 Complete Workflow

### Phase 1: Environment Setup

```bash
# 1. Start the development environment (HOST)
./devrd start

# 2. Access the container shell (HOST)
./devrd prompt

# 3. Build the project (CONTAINER)
cd /workspace
cmake -B build -S . -GNinja
ninja -C build install/strip
```

### Phase 2: SIL Simulation

```bash
# 4. List available Node-RED flows (HOST)
./devrd nodered-flows

# 5. Switch to your desired simulation flow (HOST)
./devrd nodered-flow config-sil-dc

# 6. Start the SIL simulation manually (CONTAINER)
./devrd prompt
cd /workspace/build
./run-scripts/run-sil-dc.sh
```

### Phase 3: Monitor and Control

```bash
# 7. Access the Node-RED UI
# Open: http://localhost:1881/ui
```

## Available Commands

### Environment Management

```bash
./devrd start          # Start all services (MQTT, Steve, Node-RED, etc.)
./devrd start <profile> # Start specific profile (e.g., tools, ocpp, mqtt)
./devrd stop           # Stop all services
./devrd stop <profile>  # Stop specific profile
./devrd prompt         # Access container shell
./devrd purge          # Remove all containers and volumes for current folder
./devrd purge [pattern] # Remove all containers and volumes matching pattern
```

### Node-RED Management

```bash
./devrd nodered-flows           # List available simulation flows
./devrd nodered-flow <name>     # Switch to specific flow
./devrd nodered-status          # Show current Node-RED status
```

### SIL Simulation Scripts

```bash
# Available in build/run-scripts/ after building (CONTAINER):
cd /workspace/build
./run-scripts/run-sil-dc.sh                    # Single DC charging
./run-scripts/run-sil-dc-bpt.sh                # DC charging with BPT
./run-scripts/run-sil-energy-management.sh     # Energy management
./run-scripts/run-sil-two-evse.sh              # Two EVSE simulation
./run-scripts/run-sil.sh                       # Basic SIL simulation
```

## Available Services

When you run `./setup start`, the following services become available:

| Service | URL | Purpose |
|---------|-----|---------|
| **Node-RED UI** | <http://localhost:1881/ui> | SIL simulation interface |
| **MQTT Explorer** | <http://localhost:4000> | MQTT topic browser |
| **Steve (HTTP)** | <http://localhost:8180> | OCPP backend management |

## Docker Compose Profiles

Services are organized into logical profiles for easier management:

| Profile | Services | Purpose |
|---------|----------|---------|
| `mqtt` | MQTT Server | Basic MQTT broker |
| `ocpp` | MQTT Server, OCPP DB, Steve | Complete OCPP backend |
| `tools` | MQTT Server, Node-RED, MQTT Explorer | SIL simulation tools |

## Docker Compose Project Naming

The development environment uses Docker Compose to manage services. The project name determines container naming and grouping:

### Default Behavior

- **Project name**: Uses current folder name + `_devcontainer` (e.g., `ev-ws_devcontainer` for `/path/to/ev-ws`)
- **Container names**: `{project-name}-{service}-1`
  - Example: `ev-ws_devcontainer-nodered-1`, `ev-ws_devcontainer-steve-1`, `ev-ws_devcontainer-mqtt-explorer-1`

### Custom Project Name

Override the default project name using environment variable:

```bash
# Use custom project name
DOCKER_COMPOSE_PROJECT_NAME="my-everest" ./setup start

# Result: my-everest-nodered-1, my-everest-steve-1, etc.
```

### Profile-Based Control

Start or stop service groups using profiles:

```bash
# Start tools profile (Node-RED + MQTT Explorer + MQTT)
./setup start tools

# Start OCPP profile (Steve + OCPP DB + MQTT)
./setup start ocpp

# Start only MQTT server
./setup start mqtt

# Stop tools profile
./setup stop tools
```

## Available SIL Configurations

After building the project, you can access these simulation flows:

| Flow Name | Description | Use Case |
|-----------|-------------|----------|
| `config-sil-dc` | Single DC charging simulation | Basic DC charging testing |
| `config-sil-dc-bpt` | DC charging with BPT | Bidirectional power transfer |
| `config-sil-energy-management` | Energy management simulation | Grid integration testing |
| `config-sil-two-evse` | Two EVSE simulation | Multi-EVSE scenarios |
| `config-sil` | Basic SIL simulation | General testing |

## 🎮 Step-by-Step Example: DC Charging Simulation

### 1. Start Environment

```bash
./setup start
```

**Output:**

```
Container Services Summary:
==============================
MQTT Explorer:    http://localhost:4000
Steve (HTTP):     http://localhost:8180
Steve (HTTPS):    https://localhost:8443
Node-RED UI:       http://localhost:1881/ui
```

### 2. Build Project

```bash
./setup prompt
# Inside container:
cd /workspace
cmake -B build -S . -GNinja
ninja -C build install/strip
```

### 3. List Available Flows

```bash
./setup nodered-flows
```

**Output:**

```
Available Node-RED Flows:
=============================
Found 5 flow(s):
  config-sil-dc-bpt
  config-sil-dc
  config-sil-energy-management
  config-sil
  config-sil-two-evse
```

### 4. Switch to DC Flow

```bash
./setup nodered-flow config-sil-dc
```

**Output:**

```
Switching Node-RED to flow: dc
Source: /home/docker/.cache/cpm/.../config-sil-dc-flow.json
Node-RED flow switched successfully!
Access at: http://localhost:1881/ui
```

### 5. Start SIL Simulation

```bash
# Inside container:
cd /workspace/build
./run-scripts/run-sil-dc.sh
```

### 6. Monitor and Control

Open <http://localhost:1881/ui> in your browser to:

- Monitor charging parameters
- Control charging sessions
- View real-time data
- Debug MQTT topics

## 🔍 Troubleshooting

### Node-RED Not Starting

```bash
# Check if container is running
./setup nodered-status

# If not running, restart tools profile
./setup stop tools
./setup start tools

# Or restart entire environment
./setup stop
./setup start
```

### No Flows Available

```bash
# Ensure project is built
./setup prompt
cd /workspace
cmake -B build -S . -GNinja && ninja -C build install/strip

# Outside container list the flows
./setup nodered-flows
```

### Port Conflicts

If you see port binding errors:

```bash
# Kill processes using port 1881
sudo lsof -ti:1881 | xargs sudo kill -9

# Restart tools profile or entire environment
./setup start tools
# OR
./setup start
```

### SIL Script Not Found

```bash
# Ensure you're in the container
./setup prompt

# Check if scripts exist
cd /workspace/build
ls -la run-scripts/

# If not found, rebuild
cd /workspace
cmake -B build -S . -GNinja && ninja -C build install/strip
```

## 🎯 Best Practices

### 1. **Always Build First**

The Node-RED flows are generated during the build process. Always run `cmake` and `ninja` before trying to access flows.

### 2. **Use Container Shell**

Run SIL scripts from inside the container using `./setup prompt` to ensure proper environment setup.

### 3. **Monitor Services**

Use `./setup nodered-status` to check if Node-RED is running and which flow is active.

### 4. **Service-Specific Commands**

Use profiles to manage service groups efficiently:

```bash
# Start only what you need
./setup start tools    # For SIL simulations
./setup start ocpp     # For OCPP development
./setup start mqtt     # For basic MQTT testing
```

### 5. **Custom Project Names**

Use custom project names for multiple environments:

```bash
# Different projects
DOCKER_COMPOSE_PROJECT_NAME="project-a" ./setup start
DOCKER_COMPOSE_PROJECT_NAME="project-b" ./setup start
```

### 6. **Check Logs**

If something isn't working, check the container logs:

```bash
docker logs devcontainer-nodered-1
docker logs devcontainer-devcontainer-1
```

### 7. **Start Fresh When Needed**

If you encounter issues, a clean restart often helps:

```bash
./setup stop
./setup purge
./setup start
```

### 8. **Custom Project Names**

When working with multiple projects, use custom project names to avoid conflicts:

```bash
# Different project names for different workspaces
DOCKER_COMPOSE_PROJECT_NAME="project-a" ./setup start
DOCKER_COMPOSE_PROJECT_NAME="project-b" ./setup start
```

## 🔗 Related Documentation

- **Architecture**: See `ARCHITECTURE.md` for system overview
- **API Documentation**: Check `api_specs/` for detailed API information
- **Configuration**: Review `config/` for configuration examples

## 🆘 Getting Help

If you encounter issues:

1. **Check Status**: `./setup nodered-status`
2. **Verify Build**: Ensure `cmake` and `ninja` completed successfully
3. **Check Logs**: Look at container logs for error messages
4. **Restart Clean**: Use `./setup purge` and `./setup start`
5. **Review Commands**: Run `./setup --help` for available commands

---

**Happy Simulating! 🚀**
