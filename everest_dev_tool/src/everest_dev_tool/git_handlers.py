import argparse
import logging
import subprocess

default_logger = logging.getLogger("EVerest's Development Tool - Git Helpers")

def clone_handler(args: argparse.Namespace):
    log = args.logger

    log.info(
        f"Cloning repository:\n"
        f"  Method: {args.method}\n"
        f"  Forge: {args.forge}\n"
        f"  Organization: {args.organization}\n"
        f"  Repository Name: {args.repository_name}\n"
        f"  Branch: {args.branch}\n"
    )
    repository_url = ""
    if args.method == 'https':
        repository_url = f"https://{args.forge}/"
    else:
        repository_url = f"git@{args.forge}:"
    repository_url = repository_url + f"{ args.organization }/{ args.repository_name }.git"

    cmd_args = ["git", "clone", "-b", args.branch, repository_url]

    log.debug(f"Command to execute: {' '.join(cmd_args)}")

    if args.dry:
        log.info(f"Dry run: Would execute: {' '.join(cmd_args)}")
    else:
        subprocess.run(cmd_args, check=True)
