# syntax=docker/dockerfile:1
FROM ghcr.io/everest/everest-ci/dev-env-base:v1.3.2

# Update the package list
RUN sudo apt update

# Modify the existing docker user and group to match the host's UID and GID
ARG UID=1000
ARG GID=1000
RUN groupmod --gid ${GID} docker && \
    usermod --uid ${UID} --gid ${GID} docker

# Switch to the new user
USER docker
WORKDIR /home/docker

# EVerest Development Tool - Dependencies
RUN pip install --break-system-packages \
    docker==7.1.0
# EVerest Development Tool
ARG DEV_ENV_TOOL_VERSION=feature/support_different_repo_org
# Get the latest commit hash from the specific branch/tag to bust cache when repository changes
RUN git ls-remote https://github.com/EVerest/everest-dev-environment.git ${DEV_ENV_TOOL_VERSION} | cut -f1 > /tmp/latest_commit.txt
ARG CACHE_BUST=$(cat /tmp/latest_commit.txt)
RUN python3 -m pip install --break-system-packages \
    git+https://github.com/EVerest/everest-dev-environment@${DEV_ENV_TOOL_VERSION}#subdirectory=everest_dev_tool

ARG ORGANIZATION_ARG=EVerest
ENV EVEREST_DEFAULT_ORGANIZATION=${ORGANIZATION_ARG}
ARG REPOSITORY_URL_ARG=git@github.com
ENV EVEREST_REPOSITORY_URL=${REPOSITORY_URL_ARG}

RUN echo "echo \"🏔️ 🚘 Welcome to the EVerest development environment!\"" >> /home/docker/.bashrc
RUN echo "echo \"To initialize the EVerest core repository everest-core in your workspace please run the following command:\"" >> /home/docker/.bashrc
RUN echo "echo \"everest clone everest-core\"" >> /home/docker/.bashrc
