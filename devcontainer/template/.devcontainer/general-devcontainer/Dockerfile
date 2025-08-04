# syntax=docker/dockerfile:1
FROM ghcr.io/everest/everest-ci/dev-env-base:v1.5.4

# Update the package list
RUN sudo apt update

# EVerest Development Tool - Dependencies
RUN pip install --break-system-packages \
    docker==7.1.0
# EVerest Development Tool
ARG DEV_ENV_TOOL_VERSION=everest-dev-tool-v0.1.0
RUN python3 -m pip install --break-system-packages \
    git+https://github.com/EVerest/everest-dev-environment@${DEV_ENV_TOOL_VERSION}#subdirectory=everest_dev_tool

RUN echo "echo \"🏔️ 🚘 Welcome to the EVerest development environment!\"" >> ${HOME}/.bashrc
RUN echo "echo \"To initialize the EVerest core repository everest-core in your workspace please run the following command:\"" >> ${HOME}/.bashrc
RUN echo "echo \"everest clone everest-core\"" >> ${HOME}/.bashrc
