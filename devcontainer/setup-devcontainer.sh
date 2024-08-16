#!/bin/bash

set -e

read -p "Enter the workspace directory (default is the current directory): " WORKSPACE_DIR
if [ -z "$WORKSPACE_DIR" ]; then
    WORKSPACE_DIR="./"
fi
WORKSPACE_DIR=$(realpath -m "$WORKSPACE_DIR")

read -p "Enter the version of the everest-dev-environment (default is 'main'): " VERSION
if [ -z "$VERSION" ]; then
    VERSION="main"
fi

echo "Create the workspace directory '$WORKSPACE_DIR' if it does not exist"
mkdir -p $WORKSPACE_DIR

if [ "$(ls -A $WORKSPACE_DIR)" ]; then
    # The workspace directory is not empty, warning do you want to continue?
    read -p "The workspace directory is not empty, do you want to continue? (y/N): " -r
    if [[ $REPLY =~ ^[Nn]$ || $REPLY = "" ]]; then
        echo "Exiting.."
        exit 1
    elif [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Invalid input. Exiting.."
        exit 1
    fi
fi

TMP_DIR=$(mktemp --directory)
echo "Clone the everest-dev-environment repository to the workspace directory with the version $VERSION, temporarily.."
git clone --quiet --depth 1 --single-branch --branch "$VERSION" https://github.com/EVerest/everest-dev-environment.git "$TMP_DIR"

echo "Copy the template devcontainer configuration files to the workspace directory"
cp -n -r $TMP_DIR/devcontainer/template/. $WORKSPACE_DIR/

echo "Remove the everest-dev-environment repository"
rm -rf "$TMP_DIR"
