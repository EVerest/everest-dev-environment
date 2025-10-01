#!/bin/bash

# Install bash completion for setup script

set -e

echo "🔧 Installing bash completion for setup script..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_FILE="$SCRIPT_DIR/setup-completion.bash"

# Check if completion file exists
if [ ! -f "$COMPLETION_FILE" ]; then
    echo "❌ Error: setup-completion.bash not found in $SCRIPT_DIR"
    exit 1
fi

# Make completion file executable
chmod +x "$COMPLETION_FILE"

# Determine the user's shell configuration file
SHELL_CONFIG=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_CONFIG="$HOME/.bash_profile"
else
    echo "❌ Error: Could not find .bashrc or .bash_profile in $HOME"
    exit 1
fi

# Check if completion is already installed
if grep -q "setup-completion.bash" "$SHELL_CONFIG"; then
    echo "⚠️  Bash completion already installed in $SHELL_CONFIG"
    echo "   To reinstall, remove the line containing 'setup-completion.bash' from $SHELL_CONFIG"
    exit 0
fi

# Add completion to shell config
echo "" >> "$SHELL_CONFIG"
echo "# Setup script bash completion" >> "$SHELL_CONFIG"
echo "source \"$COMPLETION_FILE\"" >> "$SHELL_CONFIG"

echo "✅ Bash completion installed successfully!"
echo "   Added to: $SHELL_CONFIG"
echo "   Completion file: $COMPLETION_FILE"
echo "   Location: .devcontainer/setup-completion.bash"
echo ""
echo "🔄 To activate completion in current session, run:"
echo "   source .devcontainer/setup-completion.bash"
echo ""
echo "📝 Available completions:"
echo "   • Commands: env, build, start, stop, prompt, purge, exec, nodered-flows, nodered-flow, nodered-status"
echo "   • Options: -v, --version, -h, --hosting, -o, --org, -w, --workspace, --help"
echo "   • Node-RED flows: dynamically detected from container"
echo "   • Directories: for workspace option"
echo "   • Common commands: for exec option"