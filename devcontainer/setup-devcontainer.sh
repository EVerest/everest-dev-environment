#!/bin/bash

set -e

# Default values
ORG="EVerest"
REPO="git@github.com"
VERSION="main"
WORKSPACE_DIR="./"
REPO_NAME="everest-dev-environment.git"

# Function to display help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -w, --workspace DIR     Workspace directory to create devcontainer in (default: $WORKSPACE_DIR)"
    echo "  -v, --version VERSION   Version of the development environment (default: $VERSION)"
    echo "  -h, --hosting URL       Git hosting URL (default: $REPO)"
    echo "  -o, --org ORGANIZATION  Organization name on the hosting platform (default: $ORG)"
    echo "  --help                  Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 -w /path/to/workspace -v release/1.0"
    echo "  $0 --workspace ./my-project --version main --hosting git@github.com --org mycompany"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workspace)
            WORKSPACE_DIR="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -h|--hosting)
            REPO="$2"
            shift 2
            ;;
        -o|--org)
            ORG="$2"
            shift 2
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# If no command line arguments were provided, prompt for values
if [ $# -eq 0 ]; then
    read -p "Enter the workspace directory (default is the current directory): " USER_WORKSPACE_DIR
    if [ -n "$USER_WORKSPACE_DIR" ]; then
        WORKSPACE_DIR="$USER_WORKSPACE_DIR"
    fi

    read -p "Enter the version of the development environment (default is 'main'): " USER_VERSION
    if [ -n "$USER_VERSION" ]; then
        VERSION="$USER_VERSION"
    fi

    read -p "Are you a customer of Pionix (or a Pionix internal developer)? (Y/n): " -r
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        # Internal developer, override default values
        ORG="PionixPro"
        REPO="git@github.com"
    else
        read -p "Are you using Pionix hosted git (default:${REPO}) or do you have your own hosting (e.g. like git@github.com)?: " USER_REPO
        read -p "What is the organization name you are using for the hosted git (default:${ORG}): " USER_ORG

        if [ -n "$USER_REPO" ]; then
            REPO="$USER_REPO"
        fi
        if [ -n "$USER_ORG" ]; then
            ORG="$USER_ORG"
        fi
    fi
fi

WORKSPACE_DIR=$(realpath -m "$WORKSPACE_DIR")

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
# Determine URL format based on hosting type
if [[ "$REPO" == *"@"* ]]; then
    # SSH format: git@github.com:org/repo.git
    CLONE_URL="$REPO:$ORG/$REPO_NAME"
else
    # HTTPS format: https://github.com/org/repo.git
    CLONE_URL="$REPO/$ORG/$REPO_NAME"
fi

echo "Clone $REPO_NAME repository ($CLONE_URL) to the workspace directory with the version $VERSION, temporarily.."
git clone --quiet --depth 1 --single-branch --branch "$VERSION" "$CLONE_URL" "$TMP_DIR"

echo "Copy the template devcontainer configuration files to the workspace directory"
cp -n -r $TMP_DIR/devcontainer/template/. $WORKSPACE_DIR/

# Replace placeholders in docker-compose.devcontainer.yml
sed -i "s|ORGANIZATION_ARG: \"REPLACE_ORG\"|ORGANIZATION_ARG: \"$ORG\"|" $WORKSPACE_DIR/.devcontainer/general-devcontainer/docker-compose.devcontainer.yml
sed -i "s|REPOSITORY_URL_ARG: \"REPLACE_URL\"|REPOSITORY_URL_ARG: \"$REPO\"|" $WORKSPACE_DIR/.devcontainer/general-devcontainer/docker-compose.devcontainer.yml

echo "Remove the temporary clone of the $REPO_NAME repository"
rm -rf "$TMP_DIR"
