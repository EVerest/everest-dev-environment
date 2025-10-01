# EVerest dev environment

This subproject contains all utility files for setting up your development environment.
So far this is the [edm - the Everest Dependency Manager](dependency_manager/README.md) which helps you orchestrating the dependencies between the different everest repositories.

You can install [edm](dependency_manager/README.md) very easy using pip.

All documentation and the issue tracking can be found in our main repository here: https://github.com/EVerest/everest
Please check as well the complete documentation at https://docs.pionix.de

## 🚀 SIL Simulation

For Command Reference, see:
- **[Command Reference](doc/COMMAND_REFERENCE.md)** - List of commands and their meaning
For Software-In-the-Loop (SIL) simulations, see:
- **[Complete SIL Guide](doc/SIL_SIMULATION_GUIDE.md)** - Detailed workflow and troubleshooting

## Quick Start

### Prerequisites
- VS Code with Docker extension
- Docker installed
- Docker compose installed version V2 (not working with V1)
Tested with Linux, specifically with Ubuntu 22.04 and 24.04.

### Setup

1. **Create a folder for your project**
    Create a new directory and navigate into it. This directory will be your new workspace or use an existing one.

    ```bash
    mkdir my-workspace
    cd my-workspace
    ```

2. **Install DevContainer template:**
   You can use the following command to download and install the devcontainer template:
   ```bash
   export BRANCH="main" && bash -c "$(curl -s --variable %BRANCH=main --expand-url https://raw.githubusercontent.com/EVerest/everest-dev-environment/{{BRANCH}}/devcontainer/template/setup)" install
   ```

   On certain systems with an older version of curl the command above will fail. In that case, you need to manually download the repository and execute the script:
   ```bash
   git clone git@github.com:EVerest/everest-dev-environment.git
   ./everest-dev-environment/devcontainer/template/setup install
   # you can delete the everest-dev-environment folder, it is not needed anymore
   rm -rf everest-dev-environment
   ```

   The script will ask you for the following information:
   1. Workspace directory: Default is the current directory. You can keep the default by pressing enter.
   2. everest-dev-environment version: Default is 'main'. You can keep the default by pressing enter.


3. **Generate environment configuration:**
   ```bash
   ./setup
   ```

4. **Open in VS Code:**
This will create the `.env` file with your repository information. Then open the workspace in Visual Studio Code:
    ```bash
    code .
    ```
Or press Ctrl+O to open the current folder in VSCode.

5. **Reopen in container** when prompted by VS Code.


### VS Code Development (Recommended)
The easiest way to develop is using VS Code with the development container:
1. Follow the [Quick Start](#quick-start) steps above
2. VS Code will automatically build the container with your repository settings
3. All development happens inside the container with the correct environment variables

The contents of `my-workspace` folder are mapped inside the container in the folder called `/workspace`.
You can exit VS Code at any time, re-running it will cause VS Code to ask you again to reopen in container.


### Manual Docker Setup

If you prefer to run the container outside VS Code, the `./setup` script provides comprehensive control:

```bash
# Quick start (generate .env and start all services)
./setup start

# Step-by-step workflow:
./setup build                  # Build container (generates .env if missing)
./setup start                  # Start all services (generates .env if missing)
./setup env                    # Generate .env file with auto-detected values
./setup env -v main            # Update specific values in existing .env
./setup stop                   # Stop all services
./setup purge                  # Remove all containers, images, and volumes

# Container access:
./setup prompt                 # Get interactive shell in container
./setup exec <command>         # Execute single command in container

# Node-RED SIL Simulation:
./setup nodered-flows          # List available simulation flows
./setup nodered-flow <name>    # Switch to specific simulation
./setup nodered-status         # Check Node-RED status

# Custom environment configuration:
./setup env -v main            # Use specific everest tool branch
./setup env -h git@git.org.com:MyOrg/everest-core.git  # Set git hosting URL (extracts host, user, org)
./setup env -w /path/to/workspace  # Set workspace directory mapping

# .env file behavior:
# - Missing/empty: Generated with auto-detection
# - Exists: Only updated when env command has specific options
# - build/start: Generate if missing, no changes if exists

### Workspace Mapping

The `/workspace` directory inside the container can be mapped to any folder on your host system:

```bash
# Default behavior (maps parent of .devcontainer, so by default your `my-workspace` folder)
./setup start

# Map to custom folder
./setup env -w ~/checkout
./setup start

# Map to current directory
./setup env -w .
./setup start

# Map to absolute path
./setup env -w /opt/tools
./setup start

# Map to relative path
./setup env -w ../other-project
./setup start
```

**Use cases:**
- **Default**: Maps the current project root (recommended for development)
- **Custom folder**: Access files from other directories inside container
- **Shared tools**: Map system directories for development tools
- **Multi-project**: Work with multiple projects simultaneously

**Important notes:**
- The folder must exist and be accessible
- Relative paths are converted to absolute paths
- The mapping persists in `.env` file for future container starts
- Only one folder can be mapped at a time

### Bash Completion (Optional)

For enhanced command-line experience, install bash completion for the setup script:

```bash
# Install completion (adds to your .bashrc)
.devcontainer/install-completion.sh

# Or source manually for current session
source .devcontainer/setup-completion.bash
```

**Available completions:**
- **Commands**: `install`, `env`, `build`, `start`, `stop`, `prompt`, `purge`, `exec`, `nodered-flows`, `nodered-flow`, `nodered-status`
- **Options**: `-v`, `--version`, `-h`, `--hosting`, `-o`, `--org`, `-w`, `--workspace`, `--help`
- **Node-RED flows**: Dynamically detected from container
- **Directories**: For workspace option
- **Common commands**: For exec option

**Example usage:**
```bash
./setup <TAB>                    # Shows all commands
./setup install <TAB>            # Shows install command
./setup nodered-flow <TAB>       # Shows available flows
./setup env -v <TAB>             # Shows version options
./setup exec <TAB>               # Shows common commands
```
```

## 🚀 SIL Simulation Quick Start

### Complete Workflow (5 minutes)
```bash
# 1. Start environment (HOST)
./setup start

# 2. Build project (CONTAINER)
./setup prompt
cd /workspace
cmake -B build -S . -GNinja && ninja -C build install/strip

# 3. Switch to simulation (HOST)
./setup nodered-flow config-sil-dc

# 4. Start simulation (CONTAINER)
./setup prompt
cd /workspace/build
./run-scripts/run-sil-dc.sh

# 5. Open UI
# Visit: http://localhost:1881/ui
```

### Available Services
| Service | URL | Purpose |
|---------|-----|---------|
| **Node-RED UI** | http://localhost:1881/ui | SIL simulation interface |
| **MQTT Explorer** | http://localhost:4000 | MQTT topic browser |
| **Steve (HTTP)** | http://localhost:8180 | OCPP backend management |

### Available Simulations
| Flow Name | Description | Script |
|-----------|-------------|--------|
| `config-sil-dc` | Single DC charging | `cd /workspace/build && ./run-scripts/run-sil-dc.sh` |
| `config-sil-dc-bpt` | DC charging with BPT | `cd /workspace/build && ./run-scripts/run-sil-dc-bpt.sh` |
| `config-sil-energy-management` | Energy management | `cd /workspace/build && ./run-scripts/run-sil-energy-management.sh` |
| `config-sil-two-evse` | Two EVSE simulation | `cd /workspace/build && ./run-scripts/run-sil-two-evse.sh` |
| `config-sil` | Basic SIL simulation | `cd /workspace/build && ./run-scripts/run-sil.sh` |

### Troubleshooting
| Issue | Solution |
|-------|----------|
| Node-RED not starting | `./setup nodered-status` then `./setup stop && ./setup start` |
| No flows available | `./setup prompt` then `cd /workspace && cmake -B build -S . -GNinja && ninja -C build install/strip` |
| Port conflicts | `sudo lsof -ti:1881 \| xargs sudo kill -9` then `./setup start` |
| SIL script not found | Ensure you're in container and project is built |

## Building EVerest

Once inside the development container:

```bash
cd /workspace
cmake -S . -B build -G Ninja
ninja -C build install/strip
```

**Note:** You can use `make` instead of `ninja` by removing `-G Ninja`.

## Working with Multiple Repositories

To work with multiple everest repositories:

1. Create a new folder and either manually clone the everest-dev-environment or use the command from QuickStart > Setup > Downloading the setup script.
2. Start VS Code or run the container manually
3. Clone additional repositories:

```bash
mkdir myworkspace
export BRANCH="main" && bash -c "$(curl -s --variable %BRANCH=main --expand-url https://raw.githubusercontent.com/EVerest/everest-dev-environment/{{BRANCH}}/devcontainer/template/setup)" install
# if the above command fails, just manually clone the repo and execute the setup script:
#    git clone git@github.com:EVerest/everest-dev-environment.git
#   ./everest-dev-environment/devcontainer/template/setup install
cd myworkspace
./setup build # generates .env if missing and build the container
code . # if you use VSCode
./setup start # not using VSCode (generates .env if missing)
./setup prompt # not using VSCode
# inside the container
cd /workspace
everest clone everest-core # or use the git command to clone
cd everest-core
cmake -S . -B build -G Ninja
ninja -C build install/strip
# this is building everest-core
# the rest of the dependencies will be automatically downloaded by edm
```

## Environment Variables

The container automatically sets these variables based on your repository:
- `EVEREST_DEV_TOOL_DEFAULT_GIT_METHOD`: ssh or http (for everest-core must be set to ssh)
- `EVEREST_DEV_TOOL_DEFAULT_GIT_HOST`: github.com or your company git host (if applicable)
- `EVEREST_DEV_TOOL_DEFAULT_GIT_SSH_USER`: the ssh default user (git or forgejo, etc)
- `EVEREST_DEV_TOOL_DEFAULT_GIT_ORGANIZATION`: EVerest (if working on the official version) or YourOrg (for customers cloning EVerest in a different git org)
- `EVEREST_TOOL_BRANCH`: branch of the everest-dev-environment repository to use (default: main)

## Troubleshooting

**Regenerate environment configuration:**
```bash
./setup env                   # Generate new .env file with auto-detection
./setup env -v main           # Update only branch in existing file
./setup env -h git@git.org.com:MyOrg/everest-core.git  # Update hosting info in existing file (extracts host, user, org)
```

**Customize environment variables:**
```bash
# Use specific branch for everest-dev-environment
./setup env -v release/1.0

# Use custom hosting URL (extracts host, user, and organization)
./setup env -h git@git.org.com:MyOrg/everest-core.git
```

**Check available services:**
```bash
everest services --help
```

**Purge clean the container, images and volumes and rebuild everything:**
```bash
./setup purge                  # Remove all resources for current folder
./setup purge my-project       # Remove all resources matching 'my-project' pattern
./setup build                  # Will generate .env if missing
```

**Note:** You might want to delete the cloned repositories (if needed).

**After git pull with container changes:**
```bash
# If you pulled changes that modify the container configuration
./setup purge                  # Remove old containers and images
./setup build                  # Rebuild with new configuration
./setup start                  # Start the updated environment
```

**Note:** This is especially important when the Dockerfile, docker-compose.yml, or other container-related files have been updated.

**Working with multiple instances or branches:**
```bash
# If you're working on multiple everest instances or branches simultaneously
# Each instance should use a different workspace directory to avoid conflicts
# You can use of course only one folder and work with multiple branches,
# this is just showing how to work with multiple folders in parallel, if necessary

# Instance 1 (main branch)
mkdir ~/everest-main
cd ~/everest-main
git clone <repository> .
./setup -w ~/everest-main

# Instance 2 (feature branch)
mkdir ~/everest-feature
cd ~/everest-feature
git clone <repository> .
git checkout feature-branch
./setup -w ~/everest-feature

# Instance 3 (different project)
mkdir ~/everest-project2
cd ~/everest-project2
git clone <different-repo> .
./setup -w ~/everest-project2
```

**Important considerations:**
- **Port conflicts**: Each instance uses the same ports (1883, 1881, 4000, etc.). Only one instance can run at a time.
- **Volume conflicts**: Docker volumes are shared. Use `./setup purge` before switching instances.
- **SSH keys**: Ensure your SSH agent has the necessary keys for all repositories.
- **Workspace isolation**: Use different workspace directories (`-w` option) for each instance.
- **Container naming**: Docker containers are named based on the workspace directory to avoid conflicts.

**Switching between instances:**
```bash
# Stop current instance
./setup stop

# Purge if switching to different branch/project
./setup purge

# Start new instance
cd ~/different-everest-directory
./setup start
```

## Bare Metal Development

### Python Prerequisites

For development outside containers, install:
```bash
python3 -m pip install protobuf grpcio-tools nanopb==0.4.8
```

### EDM Prerequisites

To be able to compile using Forgejo, you need to have edm tool at least with version 0.8.0:
```bash
edm --version
edm 0.8.0
```

### Building with Tests

```bash
cmake -Bbuild -S. -GNinja -DBUILD_TESTING=ON -DEVEREST_EXCLUDE_MODULES="Linux_Systemd_Rauc"
ninja -C build
ninja -C build test
```

### Cross-Compilation

Install the SDK as provided by Yocto (or similar).
Activate the environment (typically by sourcing the a script).

```bash
cd {...}/everest
cmake -S . -B build-cross -GNinja
  -DCMAKE_INSTALL_PREFIX=/var/everest
  -DEVC_ENABLE_CCACHE=1
  -DCMAKE_EXPORT_COMPILE_COMMANDS=1
  -DEVEREST_ENABLE_JS_SUPPORT=OFF
  -DEVEREST_ENABLE_PY_SUPPORT=OFF
  -Deverest-cmake_DIR=<absolute_path_to/everest-cmake/>

DESTDIR=dist ninja -C build-cross install/strip && \
    rsync -av build-cross/dist/var/everest root@<actual_ip_addres_of_target>:/var
```

