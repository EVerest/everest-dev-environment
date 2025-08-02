import argparse
import logging
import os

from . import services, git_handlers

log = logging.getLogger("EVerest's Development Tool")

def get_parser(version: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                      description="EVerest's Development Tool",)
    parser.add_argument('--version', action='version', version=f'%(prog)s { version }')
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    parser.set_defaults(action_handler=lambda _: parser.print_help())

    subparsers = parser.add_subparsers(help="available commands")

    # Service related commands
    services_parser = subparsers.add_parser("services", help="Service related commands", add_help=True)
    services_parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    services_subparsers = services_parser.add_subparsers(help="Service related commands")

    start_service_parser = services_subparsers.add_parser("start", help="Start a service", add_help=True)
    start_service_parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    start_service_parser.add_argument("service_name", help="Name of Service to start")
    start_service_parser.set_defaults(action_handler=services.start_service_handler)

    stop_service_parser = services_subparsers.add_parser("stop", help="Stop a service", add_help=True)
    stop_service_parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    stop_service_parser.add_argument("service_name", help="Name of Service to stop")
    stop_service_parser.set_defaults(action_handler=services.stop_service_handler)

    services_info_parser = services_subparsers.add_parser("info", help="Show information about the current environment", add_help=True)
    services_info_parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    services_info_parser.set_defaults(action_handler=services.info_handler)

    list_services_parser = services_subparsers.add_parser("list", help="List all available services", add_help=True)
    list_services_parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    list_services_parser.set_defaults(action_handler=services.list_services_handler)

    # Git related commands
    default_org = os.environ.get("EVEREST_DEFAULT_ORGANIZATION", "EVerest")
    clone_parser = subparsers.add_parser("clone", help="Clone a repository", add_help=True)
    clone_parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    clone_parser.add_argument('--organization', '--org', default=default_org, help=f"Git repository organization name, default is {default_org}")
    clone_parser.add_argument('--branch', '-b', default="main", help="Branch to checkout, default is 'main'")
    clone_parser.add_argument('--https', action='store_true', help="Use HTTPS to clone the repository, default is 'SSH'")
    clone_parser.add_argument("repository_name", help="Name of the repository to clone")
    clone_parser.set_defaults(action_handler=git_handlers.clone_handler)

    return parser

def setup_logging(verbose: bool):
    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    log.addHandler(console_handler)

def main(parser: argparse.ArgumentParser):
    args = parser.parse_args()
    args.logger = log

    setup_logging(args.verbose)

    args.action_handler(args)
