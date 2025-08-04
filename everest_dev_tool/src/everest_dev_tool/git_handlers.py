import argparse
import logging
import subprocess

default_logger = logging.getLogger("EVerest's Development Tool - Git Helpers")

def clone_handler(args: argparse.Namespace, log: logging.Logger = default_logger):
    log.debug("Running clone handler")

    repository_url = ""
    if args.method == 'https':
        repository_url = f"https://{args.forge}/"
    else:
        repository_url = f"git@{args.forge}:"
    repository_url = repository_url + f"{ args.organization }/{ args.repository_name }.git"

    subprocess.run(["git", "clone", "-b", args.branch, repository_url], check=True)
