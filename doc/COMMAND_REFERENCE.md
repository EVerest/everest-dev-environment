# EVerest DevRD Command Reference

## Environment Management

| Command | Description |
|---------|-------------|
| `./devrd start` | Start all services (MQTT, Steve, Node-RED, etc.) |
| `./devrd start <profile>` | Start specific profile (e.g., `tools`, `ocpp`, `mqtt`) |
| `./devrd stop` | Stop all services |
| `./devrd stop <profile>` | Stop specific profile |
| `./devrd purge [pattern]` | Remove all containers, images, and volumes (optional pattern, defaults to current folder name) |
| `./devrd build` | Build the development container |

## Container Access

| Command | Description |
|---------|-------------|
| `./devrd prompt` | Get interactive shell in container |
| `./devrd exec <cmd>` | Execute single command in container |

## Node-RED SIL Simulation

| Command | Description |
|---------|-------------|
| `./devrd flows` | List all available flow files in workspace |
| `./devrd flow <path>` | Switch to specific flow file using full path |

## Environment Configuration

| Command | Description |
|---------|-------------|
| `./devrd env` | Generate .env file with default values |
| `./devrd env -v main` | Use specific everest tool branch |
| `./devrd env -w <dir>` | Set workspace directory mapping |

## Docker Compose Profiles

Services are organized into logical profiles for easier management:

| Profile | Services | Purpose |
|---------|----------|---------|
| `mqtt` | MQTT Server | Basic MQTT broker |
| `ocpp` | MQTT Server, OCPP DB, Steve | Complete OCPP backend |
| `tools` | MQTT Server, Node-RED, MQTT Explorer | SIL simulation tools |

## Docker Compose Project Naming

The Docker Compose project name determines how containers are named and grouped. By default, it uses the **current folder name with _devcontainer suffix** (consistent with VSC behavior), but can be customized:

| Behavior | Description |
|----------|-------------|
| **Default** | Uses current folder name + `_devcontainer` (e.g., `ev-ws_devcontainer` for `/path/to/ev-ws`) |
| **Override** | Set `DOCKER_COMPOSE_PROJECT_NAME` environment variable |
| **Example** | `DOCKER_COMPOSE_PROJECT_NAME="my-project" ./setup start` |

**Container naming pattern:** `{project-name}-{service}-1`

- Default: `ev-ws_devcontainer-nodered-1`, `ev-ws_devcontainer-steve-1`
- Custom: `my-project-nodered-1`, `my-project-steve-1`

## SIL Simulation Scripts

*Available in `build/run-scripts/` after building:*

| Script | Description |
|--------|-------------|
| `cd /workspace/build && ./run-scripts/run-sil-dc.sh` | Single DC charging simulation |
| `cd /workspace/build && ./run-scripts/run-sil-dc-bpt.sh` | DC charging with BPT |
| `cd /workspace/build && ./run-scripts/run-sil-energy-management.sh` | Energy management simulation |
| `cd /workspace/build && ./run-scripts/run-sil-two-evse.sh` | Two EVSE simulation |
| `cd /workspace/build && ./run-scripts/run-sil.sh` | Basic SIL simulation |

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Node-RED UI** | <http://localhost:1881/ui> | SIL simulation interface |
| **MQTT Explorer** | <http://localhost:4000> | MQTT topic browser |
| **Steve (HTTP)** | <http://localhost:8180> | OCPP backend management |

## Available Flows

*Use `./devrd nodered-flows` to see all available flow files:*

| Flow File | Description |
|-----------|-------------|
| `everest-core/config/nodered/config-sil-dc-flow.json` | Single DC charging simulation |
| `everest-core/config/nodered/config-sil-dc-bpt-flow.json` | DC charging with BPT |
| `everest-core/config/nodered/config-sil-energy-management-flow.json` | Energy management simulation |
| `everest-core/config/nodered/config-sil-two-evse-flow.json` | Two EVSE simulation |
| `everest-core/config/nodered/config-sil-flow.json` | Basic SIL simulation |

**Usage Examples:**
```bash
# List all available flows
./devrd flows

# Switch to DC charging flow
./devrd flow everest-core/config/nodered/config-sil-dc-flow.json

# Switch to energy management flow
./devrd flow everest-core/config/nodered/config-sil-energy-management-flow.json
```

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Node-RED not starting | `./devrd flows` (checks container status) then `./devrd stop && ./devrd start` |
| No flows available | `./devrd prompt` then `cd /workspace && cmake -B build -S . -GNinja && ninja -C build install/strip` |
| Port conflicts | `sudo lsof -ti:1881 \| xargs sudo kill -9` then `./devrd start` |
| SIL script not found | Ensure you're in container, project is built, and you're in `/workspace/build` |

## 📖 Help

```bash
./devrd --help              # Show all available commands
./devrd flows               # List available flows
```

## Examples

```bash
# Start all services
./devrd start

# Start tools profile (Node-RED + MQTT Explorer)
./devrd start sil

# Start OCPP profile (Steve + OCPP DB + MQTT)
./devrd start ocpp

# Start only MQTT server
./devrd start mqtt

# Stop all services
./devrd stop

# Stop tools profile
./devrd stop sil

# Use custom project name
DOCKER_COMPOSE_PROJECT_NAME="my-everest" ./devrd start

# List available flows
./devrd flows

# Switch Node-RED flow using file path
./devrd flow everest-core/config/nodered/config-sil-dc-flow.json

# Purge all resources for current folder
./devrd purge

# Purge all resources matching specific pattern
./devrd purge my-project
```

---

**For detailed guides, see:**

- [Complete SIL Guide](SIL_SIMULATION_GUIDE.md)
