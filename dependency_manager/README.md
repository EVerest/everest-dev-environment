# Dependency Manager for EVerest

- [Dependency Manager for EVerest](#dependency-manager-for-everest)
  - [Install and Quick Start](#install-and-quick-start)
    - [Installing edm](#installing-edm)
    - [Enabling CPM_SOURCE_CACHE](#enabling-cpm_source_cache)
    - [Python packages needed to run edm](#python-packages-needed-to-run-edm)
  - [Setting up CMake integration](#setting-up-cmake-integration)
  - [Setting up a workspace](#setting-up-a-workspace)
  - [Updating a workspace](#updating-a-workspace)
  - [Using the EDM CMake module and dependencies.yaml](#using-the-edm-cmake-module-and-dependenciesyaml)
  - [Create a workspace config from an existing directory tree](#create-a-workspace-config-from-an-existing-directory-tree)
  - [Git information at a glance](#git-information-at-a-glance)

## Install and Quick Start
To install the **edm** dependency manager for EVerest you have to perform the following steps.

Please make sure you are running a sufficiently recent version of **Python3 (>=3.6)** and that you are able to install Python packages from source. Usually you just have to ensure that you have **pip**, **setuptools** and **wheel** available. Refer to [the Python *Installing Packages* documentation](https://packaging.python.org/tutorials/installing-packages/#requirements-for-installing-packages) for indepth guidance if any problems arise.

```bash
python3 -m pip install --upgrade pip setuptools wheel
```

### Installing edm
Now you can clone *this repository* and install **edm**:

(make sure you have set up your [ssh key](https://www.atlassian.com/git/tutorials/git-ssh) in github first!)

```bash
git clone git@github.com:EVerest/everest-dev-environment.git
cd everest-dev-environment/dependency_manager
python3 -m pip install .
edm --config ../everest-complete.yaml --workspace ~/checkout/everest-workspace
```

The last command registers the [**EDM** CMake module](#setting-up-cmake-integration) and creates a workspace in the *~/checkout/everest-workspace* directory from [a config that is shipped with this repository](../everest-complete.yaml).
The workspace will have the following structure containing all current dependencies for everest:
```bash
everest-workspace/
├── everest-core
├── everest-deploy-devkit
├── everest-dev-environment
├── everest-framework
├── everest-utils
├── liblog
├── libmodbus
├── libocpp
├── libsunspec
├── libtimer
├── open-plc-utils
├── RISE-V2G
└── workspace-config.yaml
```
The *workspace-config.yaml* contains a copy of the config that was used to create this workspace.

### Enabling CPM_SOURCE_CACHE
The **edm** dependency manager uses [CPM](https://github.com/cpm-cmake/CPM.cmake) for its CMake integration.
This means you *can* and **should** set the *CPM_SOURCE_CACHE* environment variable. This makes sure that dependencies that you do not manage in the workspace are not re-downloaded multiple times. For detailed information and other useful environment variables please refer to the [CPM Documentation](https://github.com/cpm-cmake/CPM.cmake/blob/master/README.md#CPM_SOURCE_CACHE).
```bash
export CPM_SOURCE_CACHE=$HOME/.cache/CPM
```

### Python packages needed to run edm
The following Python3 packages are needed to run the **edm** dependency manager.
If you installed **edm** using the guide above they were already installed automatically.

- Python >= 3.6
- Jinja2 >= 3.0
- PyYAML >= 5.4

## Setting up CMake integration
To use the **EDM** CMake module you **must** register it in the [CMake package registry](https://gitlab.kitware.com/cmake/community/-/wikis/doc/tutorials/Package-Registry#user).
You can use the following command to achieve this:

```bash
edm --register-cmake-module
```
This will create a file at *~/.cmake/packages/EDM/edm* that points to the directory in which the **EDM** CMake module has been installed.
You probably have to do this only once after the initial installation, but be advised that this might have to be done again if you reinstall **edm** with a different version of Python.

## Setting up a workspace
A sample workspace config, [everest-complete.yaml](../everest-complete.yaml), for the EVerest project is provided in the root directory of this repository.
You can set up this workspace with the following command.

```bash
edm --register-cmake-module --config ../everest-complete.yaml --workspace ~/checkout/everest-workspace
```

## Updating a workspace
To update a workspace you can edit the *workspace-config.yaml* file in the root of the workspace. You can then use the following command to apply these changes.
```bash
edm --workspace ~/checkout/everest-workspace --update
```
If you are currently in the *everest-workspace* directory the following command has the same effect.
```bash
edm --update
```

Be advised that even if you remove a repository from the config file it WILL NOT be deleted from the workspace.

An attempt will be made to switch branches to the ones specified in the config, however this will be aborted if the repository is *dirty*.

Repositories also WILL NOT be pulled, you should check the state of your repositories afterwards with the commands described in [Git information at a glance](#git-information-at-a-glance)
## Using the EDM CMake module and dependencies.yaml
To use **edm** from CMake you have to add the following line to the top-level *CMakeLists.txt* file in the respective source repository:
```cmake
find_package(EDM REQUIRED)
```
The **EDM** CMake module will be discovered automatically if you [registered the CMake module in the way it described in the *Setting up CMake integration* section of this readme](#setting-up-cmake-integration).

To define dependencies you can now add a **dependencies.yaml** file to your source repository. It should look like this:
```yaml
---
liblog:
  git: git@github.com:EVerest/liblog.git
  git_tag: main
  options: ["BUILD_EXAMPLES OFF"]
libtimer:
  git: git@github.com:EVerest/libtimer.git
  git_tag: main
  options: ["BUILD_EXAMPLES OFF"]

```

If you want to automatically check out certain dependencies into a *workspace* you can add a **workspace.yaml** file to the root of your source repository. It should look like this:
```yaml
---
workspace: ~/workspace
local_dependencies:
  liblog:
  libtimer:

```

You can overwrite the git_tag in your **workspace.yaml**, so you can use a development version in your workspace:
```yaml
---
workspace: ~/workspace
local_dependencies:
  liblog:
    git_tag: devel
  timer:

```

## Create a workspace config from an existing directory tree
Suppose you already have a directory tree that you want to save into a config file.
You can do this with the following command:
```bash
edm --create-config custom-config.yaml
```

This is a short form of
```bash
edm --create-config custom-config.yaml --include-remotes git@github.com:EVerest/*
```
and only includes repositories from the *EVerest* namespace. You can add as many remotes to this list as you want.

For example if you only want to include certain repositories you can use the following command.
```bash
edm --create-config custom-config.yaml --include-remotes git@github.com:EVerest/everest* git@github.com:EVerest/liblog.git
```

If you want to include all repositories, including external dependencies, in the config you can use the following command.
```bash
edm --create-config custom-config.yaml --external-in-config
```

## Git information at a glance
You can get a list of all git repositories in the current directory and their state using the following command.
```bash
edm --git-info --git-fetch
```
If you want to know the state of all repositories in a workspace you can use the following command.
```bash
edm --workspace ~/checkout/everest-workspace --git-info --git-fetch
```

This creates output that is similar to the following example.
```bash
[edm]: Git info for "~/checkout/everest-workspace":
[edm]: Using git-fetch to update remote information. This might take a few seconds.
[edm]: "everest-dev-environment" @ branch: main [remote: origin/main] [behind 6] [clean]
[edm]: "everest-framework" @ branch: main [remote: origin/main] [dirty]
[edm]: "everest-deploy-devkit" @ branch: main [remote: origin/main] [clean]
[edm]: "libtimer" @ branch: main [remote: origin/main] [dirty]
[edm]: 2/4 repositories are dirty.
```
