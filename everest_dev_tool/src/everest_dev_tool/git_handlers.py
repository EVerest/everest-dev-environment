import argparse
import logging
import subprocess
import os

default_logger = logging.getLogger("EVerest's Development Tool - Git Helpers")

def clone_handler(args: argparse.Namespace, log: logging.Logger = default_logger):
    log.debug("Running clone handler")

    if args.https:
        repository_url = os.environ.get("EVEREST_REPOSITORY_URL", "https://github.com/")
    else:
        repository_url = os.environ.get("EVEREST_REPOSITORY_URL", "git@github.com:")
    repository_url = repository_url + f"{ args.organization }/{ args.repository_name }.git"

    subprocess.run(["git", "clone", "-b", args.branch, repository_url], check=True)
