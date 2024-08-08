import argparse
import logging
import os,sys
import subprocess
from dataclasses import dataclass
from typing import List
import docker
import enum

@dataclass
class DockerEnvironmentInfo:
    container_id: str | None = None
    container_name: str | None = None

    container_image: str | None = None
    container_image_id: str | None = None
    container_image_digest: str | None = None

    compose_files: List[str] | None = None
    compose_project_name: str | None = None

    in_docker_container: bool = False

@dataclass
class DockerComposeCommand:
    class Command(enum.Enum):
        UP = "up"
        DOWN = "down"
        PS = "ps"
    compose_files: List[str]
    project_name: str
    command: Command
    services: List[str] | None = None
    def execute_command(self, log: logging.Logger):
        command_list = ["docker", "compose"]
        for compose_file in self.compose_files:
            command_list.extend(["-f", compose_file])
        command_list.extend(["-p", self.project_name])
        if self.command == DockerComposeCommand.Command.UP:
            command_list.extend(["up", "-d"])
            command_list.extend(self.services)
        elif self.command == DockerComposeCommand.Command.DOWN:
            command_list.extend(["down"])
            command_list.extend(self.services)
        elif self.command == DockerComposeCommand.Command.PS:
            command_list.extend(["ps"])
        else:
            log.error(f"Unknown command {self.command}")
            return
        log.debug(f"Executing command: {' '.join(command_list)}")
        subprocess.run(command_list, check=True)

@dataclass
class Service:
    """Class to represent a service"""
    name: str
    description: str
    start_command: List[str] | DockerComposeCommand
    stop_command: List[str] | DockerComposeCommand

####################
# Helper functions #
####################

def get_docker_environment_info(log: logging.Logger) -> DockerEnvironmentInfo:
    dei = DockerEnvironmentInfo()
    
    # Check if we are running in a docker container
    if not os.path.exists("/.dockerenv"):
        log.debug("Not running in Docker Container")
        dei.in_docker_container = False
        return dei

    log.debug("Running in Docker Container")

    dei.in_docker_container = True
    
    # Get the container information
    dei.container_id = subprocess.run(["hostname"], stdout=subprocess.PIPE).stdout.decode().strip()
    client = docker.from_env()
    dei.container_name = client.containers.get(dei.container_id).name

    # Get the image information
    dei.container_image = client.containers.get(dei.container_id).image.tags[0]#
    dei.container_image_id = client.containers.get(dei.container_id).image.id
    dei.container_image_digest = client.images.get(dei.container_image_id).id

    # Get the compose information
    if not os.path.exists("/workspace/.devcontainer/docker-compose.yml"):
        log.error("docker-compose.yml not found in /workspace/.devcontainer")
        sys.exit(1)
    dei.compose_files = ["/workspace/.devcontainer/docker-compose.yml"]

    # Check if the container is part of a docker-compose project
    if "com.docker.compose.project" not in client.containers.get(dei.container_id).attrs["Config"]["Labels"]:
        log.error("Container is not part of a docker-compose project")
        sys.exit(1)
    
    dei.compose_project_name = client.containers.get(dei.container_id).attrs["Config"]["Labels"]["com.docker.compose.project"]

    return dei

def get_services(docker_env_info: DockerEnvironmentInfo, log: logging.Logger) -> List[Service]:
    return [
        Service(
            name="mqtt-server",
            description="MQTT Server",
            start_command=DockerComposeCommand(
                compose_files=docker_env_info.compose_files,
                project_name=docker_env_info.compose_project_name,
                services=["mqtt-server"],
                command=DockerComposeCommand.Command.UP
            ),
            stop_command=DockerComposeCommand(
                compose_files=docker_env_info.compose_files,
                project_name=docker_env_info.compose_project_name,
                services=["mqtt-server"],
                command=DockerComposeCommand.Command.DOWN
            )
        ),
        Service(
            name="steve",
            description="OCPP server for development of OCPP 1.6",
            start_command=DockerComposeCommand(
                compose_files=docker_env_info.compose_files,
                project_name=docker_env_info.compose_project_name,
                services=["steve"],
                command=DockerComposeCommand.Command.UP
            ),
            stop_command=DockerComposeCommand(
                compose_files=docker_env_info.compose_files,
                project_name=docker_env_info.compose_project_name,
                services=["steve", "ocpp-db"],
                command=DockerComposeCommand.Command.DOWN
            )
        ),
        Service(
            name="mqtt-explorer",
            description="Web based MQTT Client to inspect mqtt traffic",
            start_command=DockerComposeCommand(
                compose_files=docker_env_info.compose_files,
                project_name=docker_env_info.compose_project_name,
                services=["mqtt-explorer"],
                command=DockerComposeCommand.Command.UP
            ),
            stop_command=DockerComposeCommand(
                compose_files=docker_env_info.compose_files,
                project_name=docker_env_info.compose_project_name,
                services=["mqtt-explorer"],
                command=DockerComposeCommand.Command.DOWN
            )
        )
    ]

def get_service_by_name(service_name: str, docker_env_info: DockerEnvironmentInfo, log: logging.Logger) -> Service:
    return next((service for service in get_services(docker_env_info, log) if service.name == service_name), None)

############
# Handlers #
############

def start_service_handler(args: argparse.Namespace):
    log = args.logger
    docker_env_info = get_docker_environment_info(log)
    service = get_service_by_name(args.service_name, docker_env_info, log)
    if service is None:
        log.error(f"Service {args.service_name} not found, try 'everest services list' to get a list of available services")
        return
    
    log.info(f"Starting service {service.name}")
    if isinstance(service.start_command, DockerComposeCommand):
        service.start_command.execute_command(log)
    else:
        subprocess.run(service.start_command, check=True)

def stop_service_handler(args: argparse.Namespace):
    log = args.logger
    docker_env_info = get_docker_environment_info(log)
    service = get_service_by_name(args.service_name, docker_env_info, log)
    if service is None:
        log.error(f"Service {args.service_name} not found, try 'everest services list' to get a list of available services")
        return
    
    log.info(f"Stopping service {service.name}")
    if isinstance(service.stop_command, DockerComposeCommand):
        service.stop_command.execute_command(log)
    else:
        subprocess.run(service.stop_command, check=True)
    
def list_services_handler(args: argparse.Namespace):
    log = args.logger
    docker_env_info = get_docker_environment_info(log)
    log.info("Available services:")
    for service in get_services(docker_env_info, log):
        log.info(f"{service.name}: {service.description}")
        log.debug(f"Start Command: {service.start_command}")
        log.debug(f"Stop Command: {service.stop_command}")

def info_handler(args: argparse.Namespace):
    log = args.logger
    docker_env_info = get_docker_environment_info(log)
    command = DockerComposeCommand(
        compose_files=docker_env_info.compose_files,
        project_name=docker_env_info.compose_project_name,
        command=DockerComposeCommand.Command.PS
    )
    command.execute_command(log)
