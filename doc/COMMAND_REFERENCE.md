# 📋 Basecamp Command Reference

## 🚀 Environment Management

| Command | Description |
|---------|-------------|
| `./setup start` | Start all services (MQTT, Steve, Node-RED, etc.) |
| `./setup start <service>` | Start specific service (e.g., `nodered`, `steve`, `mqtt-explorer`) |
| `./setup stop` | Stop all services |
| `./setup stop <service>` | Stop specific service |
| `./setup purge [pattern]` | Remove all containers, images, and volumes (optional pattern, defaults to current folder name) |
| `./setup build` | Build the development container |

## 🐚 Container Access

| Command | Description |
|---------|-------------|
| `./setup prompt` | Get interactive shell in container |
| `./setup exec <cmd>` | Execute single command in container |

## 🌐 Node-RED SIL Simulation

| Command | Description |
|---------|-------------|
| `./setup nodered-flows` | List available simulation flows |
| `./setup nodered-flow <name>` | Switch to specific simulation flow |
| `./setup nodered-status` | Show Node-RED status and current flow |

## ⚙️ Environment Configuration

| Command | Description |
|---------|-------------|
| `./setup env` | Generate .env file with auto-detected values |
| `./setup env -v main` | Use specific everest tool branch |
| `./setup env -h <url>` | Set git hosting URL |
| `./setup env -w <dir>` | Set workspace directory mapping |

## 🐳 Docker Compose Project Naming

The Docker Compose project name determines how containers are named and grouped. By default, it uses the **current folder name with _devcontainer suffix** (consistent with VSC behavior), but can be customized:

| Behavior | Description |
|----------|-------------|
| **Default** | Uses current folder name + `_devcontainer` (e.g., `ev-ws_devcontainer` for `/path/to/ev-ws`) |
| **Override** | Set `DOCKER_COMPOSE_PROJECT_NAME` environment variable |
| **Example** | `DOCKER_COMPOSE_PROJECT_NAME="my-project" ./setup start` |

**Container naming pattern:** `{project-name}-{service}-1`
- Default: `ev-ws_devcontainer-nodered-1`, `ev-ws_devcontainer-steve-1`
- Custom: `my-project-nodered-1`, `my-project-steve-1`

## 🔧 SIL Simulation Scripts

*Available in `build/run-scripts/` after building:*

| Script | Description |
|--------|-------------|
| `cd /workspace/build && ./run-scripts/run-sil-dc.sh` | Single DC charging simulation |
| `cd /workspace/build && ./run-scripts/run-sil-dc-bpt.sh` | DC charging with BPT |
| `cd /workspace/build && ./run-scripts/run-sil-energy-management.sh` | Energy management simulation |
| `cd /workspace/build && ./run-scripts/run-sil-two-evse.sh` | Two EVSE simulation |
| `cd /workspace/build && ./run-scripts/run-sil.sh` | Basic SIL simulation |

## 🌐 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Node-RED UI** | http://localhost:1881/ui | SIL simulation interface |
| **MQTT Explorer** | http://localhost:4000 | MQTT topic browser |
| **Steve (HTTP)** | http://localhost:8180 | OCPP backend management |

## 📊 Available Flows

*After building with `cmake` and `ninja`:*

| Flow Name | Description |
|-----------|-------------|
| `config-sil-dc` | Single DC charging simulation |
| `config-sil-dc-bpt` | DC charging with BPT |
| `config-sil-energy-management` | Energy management simulation |
| `config-sil-two-evse` | Two EVSE simulation |
| `config-sil` | Basic SIL simulation |



## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Node-RED not starting | `./setup nodered-status` then `./setup stop && ./setup start` |
| No flows available | `./setup prompt` then `cd /workspace && cmake -B build -S . -GNinja && ninja -C build install/strip` |
| Port conflicts | `sudo lsof -ti:1881 \| xargs sudo kill -9` then `./setup start` |
| SIL script not found | Ensure you're in container, project is built, and you're in `/workspace/build` |

## 📖 Help

```bash
./setup --help              # Show all available commands
./setup nodered-status      # Check Node-RED status
./setup nodered-flows       # List available flows
```

## 💡 Examples

```bash
# Start all services
./setup start

# Start only Node-RED
./setup start nodered

# Stop all services
./setup stop

# Stop only Steve service
./setup stop steve

# Use custom project name
DOCKER_COMPOSE_PROJECT_NAME="my-everest" ./setup start

# Switch Node-RED flow
./setup nodered-flow config-sil-dc

# Purge all resources for current folder
./setup purge

# Purge all resources matching specific pattern
./setup purge my-project
```

---

**For detailed guides, see:**
- [Complete SIL Guide](SIL_SIMULATION_GUIDE.md)