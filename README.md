# EVerest dev environment

This subproject contains all utility files for setting up your development environment. So far this is the [edm - the Everest Dependency Manager](dependency_manager/README.md) which helps you orchestrating the dependencies between the different everest repositories.

You can install [edm](dependency_manager/README.md) very easy using pip.

All documentation and the issue tracking can be found in our main repository here: https://github.com/EVerest/everest

## Easy Dev Environment Setup

To setup a devcontainer in your workspace you can use the following command to run the `setup_devcontainer.sh` script locally.

### 1. Prerequisites

Create a new directory and navigate into it. This directory will be your new workspace or use an existing one.

```bash
mkdir my-workspace
cd my-workspace
```

### 2. Run the setup script

Run the following command to setup the devcontainer.

```bash
export BRANCH="main" && bash -c "$(curl -s --variable %BRANCH=main --expand-url https://raw.githubusercontent.com/EVerest/everest-dev-environment/{{BRANCH}}/devcontainer/setup-devcontainer.sh)"
```

The script will ask you for the following information:
1. Workspace directory: Default is the current directory. You can keep the default by pressing enter.
2. everest-dev-environment version: Default is 'main'. You can keep the default by pressing enter.

### 3. Open in VS Code

After the script has finished, open the workspace in Visual Studio Code.

```bash
code .
```

VS Code will ask you to reopen the workspace in a container. Click on the button `Reopen in Container`.

### 4. Getting started

As your set up dev environment suggests when you open a terminal, you can setup your EVerest workspace by running the following command:

```bash
everest clone everest-core
```
