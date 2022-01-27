#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 - 2022 Pionix GmbH and Contributors to EVerest
#
"""Everest Dependency Manager."""
import argparse
import logging
import json
from jinja2 import Environment, FileSystemLoader
import yaml
import os
from pathlib import Path, PurePath
import subprocess
import sys
import shutil


log = logging.getLogger("edm")


class LocalDependencyCheckoutError(Exception):
    """Exception thrown when a dependency could not be checked out."""


def install_cmake():
    """Install required CMake modules into the users cmake packages path."""
    cmake_package_registry_path = Path.home() / ".cmake" / "packages" / "EDM"
    cmake_package_registry_path.mkdir(parents=True, exist_ok=True)
    edm_package_registry_file_path = cmake_package_registry_path / "edm"
    cmake_files_path = Path(__file__).parent / "cmake"
    log.debug(f"Storing EDM CMake path \"{cmake_files_path}\" "
              f"in CMake package registry \"{edm_package_registry_file_path}\".")
    with open(edm_package_registry_file_path, 'w', encoding='utf-8') as edm_package_registry_file:
        edm_package_registry_file.write(f"{cmake_files_path}")


def install_bash_completion(path=Path("~/.local/share/bash-completion")):
    """Install bash completion to a user provided path."""
    source_bash_completion_file_path = Path(__file__).parent / "edm-completion.bash"
    target_bash_completion_dir = path.expanduser()
    target_bash_completion_dir_file_path = target_bash_completion_dir / "edm.sh"
    bash_completion_in_home = Path("~/.bash_completion").expanduser()
    if not target_bash_completion_dir.exists():
        target_bash_completion_dir.expanduser().mkdir(parents=True, exist_ok=True)
    shutil.copy(source_bash_completion_file_path, target_bash_completion_dir_file_path)
    log.debug("Updated edm bash completion file")

    if not bash_completion_in_home.exists():
        with open(bash_completion_in_home, 'w', encoding='utf-8') as bash_completion_dotfile:
            bash_completion_dotfile.write("for bash_completion_file in ~/.local/share/bash-completion/* ; do\n"
                                          "    [ -f \"$bash_completion_file\" ] && . $bash_completion_file\n"
                                          "done")
            log.info(f"Updated \"{bash_completion_in_home}\" to point to edm bash completion "
                     f"in \"{target_bash_completion_dir}\"")
    else:
        log.warning(f"\"{bash_completion_in_home}\" exists, could not automatically install bash-completion")
        log.info("Please add the following entry to your .bashrc:")
        log.info(f". {target_bash_completion_dir}/edm.sh")


class Color:
    """Represents a subset of terminal color codes for use in log messages."""

    DEFAULT = ""
    CLEAR = "\033[0m"
    BLACK = "\033[30m"
    GREY = "\033[90m"
    WHITE = "\033[37m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

    @classmethod
    def set_none(cls):
        """Remove the color codes for no-color mode."""
        Color.DEFAULT = ""
        Color.CLEAR = ""
        Color.BLACK = ""
        Color.GREY = ""
        Color.WHITE = ""
        Color.RED = ""
        Color.GREEN = ""
        Color.BLUE = ""
        Color.YELLOW = ""
        Color.MAGENTA = ""
        Color.CYAN = ""


class ColorFormatter(logging.Formatter):
    """Logging formatter that uses pre-configured colors for different logging levels."""

    def __init__(self, color=True, formatting_str="[%(name)s]: %(message)s"):
        """Initialize the ColorFormatter."""
        super().__init__()
        self.color = color
        if not color:
            Color.set_none()
        self.formatting_str = formatting_str
        self.colored_formatting_strings = {
            logging.DEBUG: self.build_colored_formatting_string(Color.GREY),
            logging.INFO: self.build_colored_formatting_string(Color.CLEAR),
            logging.WARNING: self.build_colored_formatting_string(Color.YELLOW),
            logging.ERROR: self.build_colored_formatting_string(Color.RED),
            logging.CRITICAL: self.build_colored_formatting_string(Color.MAGENTA),
        }

    def build_colored_formatting_string(self, color: Color) -> str:
        """Build a formatting string with the provided color."""
        if self.color:
            return f"{color}{self.formatting_str}{Color.CLEAR}"
        return f"{self.formatting_str}"

    def format(self, record):
        """Format a record with the colored formatter."""
        return logging.Formatter(self.colored_formatting_strings[record.levelno]).format(record)


def quote(lst: list) -> list:
    """Put quotation marks around every list element, which is assumed to be a str."""
    return [f"\"{element}\"" for element in lst]


def prettify(lst: list, indent: int) -> str:
    """Construct string from list elements with the given indentation."""
    output = ""
    space = " " * indent
    for out in lst:
        if out and out != "\n":
            if len(output) > 0:
                output += f"\n{space}{out}"
            else:
                output += f"{space}{out}"
    return output


def pretty_print(lst: list, indent: int):
    """Debug log every list element with the given indentation."""
    space = " " * indent
    for out in lst:
        if out and out != "\n":
            log.debug(f"{space}{out}")


def pretty_print_process(c: subprocess.CompletedProcess, indent: int):
    """Pretty print stdout and stderr of a CompletedProcess object."""
    stdout = c.stdout.decode("utf-8").split("\n")
    pretty_print(stdout, indent)

    stderr = c.stderr.decode("utf-8").split("\n")
    pretty_print(stderr, indent)


def pattern_matches(string: str, patterns: list) -> bool:
    """Return true if one of the patterns match with the string, false otherwise."""
    matches = False
    for pattern in patterns:
        if PurePath(string).match(pattern):
            log.debug(f"Pattern \"{pattern}\" accepts string \"{string}\"")
            matches = True
            break
    return matches


class GitInfo:
    """Provide information about git repositories."""

    @classmethod
    def is_repo(cls, path: Path) -> bool:
        """Return true if path is a top-level git repo."""
        try:
            result = subprocess.run(["git", "-C", path, "rev-parse", "--git-dir"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            repo_dir = result.stdout.decode("utf-8").replace("\n", "")
            if repo_dir == ".git":
                return True
        except subprocess.CalledProcessError:
            return False
        return False

    @classmethod
    def is_dirty(cls, path: Path) -> bool:
        """Use git diff to check if the provided directory has uncommitted changes, ignoring untracked files."""
        try:
            subprocess.run(["git", "-C", path, "diff", "--quiet", "--exit-code"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            subprocess.run(["git", "-C", path, "diff", "--cached", "--quiet", "--exit-code"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return False
        except subprocess.CalledProcessError:
            return True

    @classmethod
    def is_detached(cls, path: Path) -> bool:
        """Check if the git repo at path is in detached HEAD state."""
        try:
            subprocess.run(["git", "-C", path, "symbolic-ref", "-q", "HEAD"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return False
        except subprocess.CalledProcessError:
            return True

    @classmethod
    def fetch(cls, path: Path) -> bool:
        """
        Return true if git-fetch was successful, false if not.

        TODO: distinguish between error codes?
        """
        log.debug(f"\"{path.name}\": fetching information from remote. This might take a few seconds.")
        try:
            subprocess.run(["git", "-C", path, "fetch"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError as result:
            log.error(f"\"{path.name}\" Error during git-fetch: {result.returncode}")
            return False

    @classmethod
    def pull(cls, path: Path) -> bool:
        """
        Return true if git-pull was successful, false if not.

        TODO: distinguish between error codes?
        """
        log.info(f"\"{path.name}\": pulling from remote. This might take a few seconds.")
        try:
            subprocess.run(["git", "-C", path, "pull"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError as result:
            pretty_stderr = prettify(result.stderr.decode("utf-8").split("\n"), 4)
            log.error(f"\"{path.name}\" Error during git-pull: {result.returncode}\n{pretty_stderr}")
            return False

    @classmethod
    def get_behind(cls, path: Path) -> str:
        """Return how many commits behind the repo at path is relative to remote."""
        behind = ""
        try:
            result = subprocess.run(["git", "-C", path, "rev-list", "--count", "HEAD..@{u}"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            behind = result.stdout.decode("utf-8").replace("\n", "")
        except subprocess.CalledProcessError:
            return behind

        return behind

    @classmethod
    def get_ahead(cls, path: Path) -> str:
        """Return how many commits ahead the repo at path is relative to remote."""
        ahead = ""
        try:
            result = subprocess.run(["git", "-C", path, "rev-list", "--count", "@{u}..HEAD"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            ahead = result.stdout.decode("utf-8").replace("\n", "")
        except subprocess.CalledProcessError:
            return ahead

        return ahead

    @classmethod
    def get_tag(cls, path: Path) -> str:
        """Return the current tag of the repo at path, or an empty str."""
        tag = ""
        try:
            result = subprocess.run(["git", "-C", path, "describe", "--exact-match", "--tags"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            tag = result.stdout.decode("utf-8").replace("\n", "")
        except subprocess.CalledProcessError:
            return tag

        return tag

    @classmethod
    def get_branch(cls, path: Path) -> str:
        """Return the current branch of the repo at path, or an empty str."""
        branch = ""
        try:
            result = subprocess.run(["git", "-C", path, "symbolic-ref", "--short", "-q", "HEAD"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            branch = result.stdout.decode("utf-8").replace("\n", "")
        except subprocess.CalledProcessError:
            return branch

        return branch

    @classmethod
    def get_remote_branch(cls, path: Path) -> str:
        """Return. the remote of the current branch of the repo at path, or an empty str."""
        remote_branch = ""
        try:
            result = subprocess.run(["git", "-C", path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            remote_branch = result.stdout.decode("utf-8").replace("\n", "")
        except subprocess.CalledProcessError:
            return remote_branch

        return remote_branch

    @classmethod
    def get_git_info(cls, path: Path, fetch=False) -> dict:
        """
        Return useful information about a repository a the given path.

        TODO: return type should be a well defined object
        Returns an empty dictionary if the path is no git repo
        """
        git_info = {}
        subdirs = list(path.glob("*/"))
        for subdir in subdirs:
            subdir_path = Path(subdir)
            repo_info = {'is_repo': False}
            if GitInfo.is_repo(subdir_path):
                repo_info["is_repo"] = True
                if fetch:
                    repo_info["fetch_worked"] = GitInfo.fetch(subdir_path)
                repo_info["remote_branch"] = GitInfo.get_remote_branch(subdir_path)
                repo_info["behind"] = GitInfo.get_behind(subdir_path)
                repo_info["ahead"] = GitInfo.get_ahead(subdir_path)
                repo_info["tag"] = GitInfo.get_tag(subdir_path)
                repo_info["branch"] = GitInfo.get_branch(subdir_path)
                repo_info["dirty"] = GitInfo.is_dirty(subdir_path)
                repo_info["detached"] = GitInfo.is_detached(subdir_path)

            git_info[subdir] = repo_info
        return git_info

    @classmethod
    def pull_all(cls, path: Path, repos=None) -> dict:
        """Pull all repositories in the given path, or a specific list of repos."""
        git_info = {}
        subdirs = list(path.glob("*/"))
        for subdir in subdirs:
            subdir_path = Path(subdir)
            if repos is not None and len(repos) > 0 and subdir_path.name not in repos:
                log.debug(f"Skipping {subdir_path.name} because it is not in the list of provided repos.")
                continue
            pull_info = {'is_repo': False}
            if GitInfo.is_repo(subdir_path):
                pull_info["is_repo"] = True
                pull_info["pull_worked"] = GitInfo.pull(subdir_path)

            git_info[subdir] = pull_info
        return git_info


class EDM:
    """Provide dependecy management functionality."""

    @classmethod
    def show_git_info(cls, working_dir: Path, workspace: str, git_fetch: bool):
        """Log information about git repositories."""
        git_info_working_dir = working_dir
        if workspace:
            git_info_working_dir = Path(workspace).expanduser().resolve()
            log.info("Workspace provided, executing git-info in workspace")
        log.info(f"Git info for \"{git_info_working_dir}\":")
        if git_fetch:
            log.info("Using git-fetch to update remote information. This might take a few seconds.")
        git_info = GitInfo.get_git_info(git_info_working_dir, git_fetch)

        dirty_count = 0
        repo_count = 0
        for path, info in git_info.items():
            if not info["is_repo"]:
                log.debug(f"\"{path.name}\" is not a git repository.")
                continue
            repo_count += 1
            tag_or_branch = ""
            if info["tag"]:
                tag_or_branch += f" @ tag: {info['tag']}"
            if info["branch"]:
                tag_or_branch += f" @ branch: {info['branch']}"

            remote_info = ""
            if info["detached"]:
                remote_info = f" [{Color.YELLOW}detached HEAD{Color.CLEAR}]"
            else:
                if "branch" in info and "remote_branch" in info:
                    remote_info = (f" [remote: {Color.RED}{info['remote_branch']}{Color.CLEAR}]")
                    behind_ahead = ""
                    if "behind" in info and info["behind"] and info["behind"] != "0":
                        behind_ahead += f"behind {Color.RED}{info['behind']}{Color.CLEAR}"
                    if "ahead" in info and info["ahead"] and info["ahead"] != "0":
                        if behind_ahead:
                            behind_ahead += " "
                        behind_ahead += f"ahead {Color.GREEN}{info['ahead']}{Color.CLEAR}"
                    if behind_ahead:
                        remote_info += f" [{behind_ahead}]"
            dirty = f"[{Color.GREEN}clean{Color.CLEAR}]"
            if info["dirty"]:
                dirty = f"[{Color.RED}dirty{Color.CLEAR}]"
                dirty_count += 1

            log.info(f"\"{Color.GREEN}{path.name}{Color.CLEAR}\"{tag_or_branch}{remote_info} {dirty}")

        if dirty_count > 0:
            log.info(f"{dirty_count}/{repo_count} repositories are dirty.")

    @classmethod
    def setup_workspace_from_config(cls, workspace: str, config: str, update: bool, create_vscode_workspace: bool):
        """Setup a workspace from the provided config, update an existing workspace if specified."""
        workspace_dir = Path(workspace).expanduser().resolve()

        config_path = Path(config).expanduser().resolve()
        if config_path.exists():
            log.info(f"Using config \"{config_path}\"")
        else:
            log.error(f"Config file \"{config_path}\" does not exists, stopping.")
            sys.exit(1)
        config = parse_config(config_path)
        try:
            workspace_checkout = setup_workspace(workspace_dir, config, update)
        except LocalDependencyCheckoutError:
            log.error("Could not setup workspace. Stopping.")
            sys.exit(1)
        # copy config into workspace
        try:
            config_destination_path = workspace_dir / "workspace-config.yaml"
            shutil.copyfile(config_path, config_destination_path)
            log.info(f"Copied config into \"{config_destination_path}\"")
        except shutil.SameFileError:
            log.info(f"Did not copy workspace config because source and destination are the same \"{config_path}\"")

        if create_vscode_workspace:
            create_vscode_workspace(workspace_dir, workspace_checkout)

    @classmethod
    def config_from_dependencies(cls, dependencies: dict, external_in_config: bool, include_remotes: list) -> dict:
        """Assemble a config from the given dependencies."""
        new_config = {}
        if external_in_config:
            new_config = {**new_config, **dependencies}
            log.debug("Including external dependencies in generated config.")
        else:
            for name, entry in dependencies.items():
                if pattern_matches(entry["git"], include_remotes):
                    log.debug(f"Adding \"{name}\" to config. ")
                    new_config[name] = entry
                else:
                    log.debug(f"Did not add \"{name}\" to generated config because it is an external dependency.")

        return new_config

    @classmethod
    def create_config(cls, working_dir: Path, new_config: dict, external_in_config: bool, include_remotes: list) -> dict:
        """Scan all first-level subdirectories in working_dir for git repositories that might have been missed."""
        for subdir in list(working_dir.glob("*/")):
            subdir_path = Path(subdir)
            name = subdir_path.name
            if name in new_config:
                log.debug(f"Skipping {name} which already is in config.")
                continue
            # FIXME: change this when we support alias info for a repo.
            # then this name might not be not equal to the dep name anymore
            if not subdir_path.is_dir():
                log.debug(f"Skipping {name} because it is not a directory.")
                continue
            log.debug(f"Checking {subdir_path}: {subdir_path.name}")

            entry = {}

            try:
                remote_result = subprocess.run(["git", "-C", subdir_path, "config", "--get", "remote.origin.url"],
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except subprocess.CalledProcessError:
                log.warning(f"Skipping {name} because remote could not be determined.")
                continue
            remote = remote_result.stdout.decode("utf-8").replace("\n", "")
            log.debug(f"  remote: {remote}")
            if not external_in_config and not pattern_matches(remote, include_remotes):
                log.debug(f"Skipping {name} because it is an external dependency.")
                continue
            entry["git"] = remote
            # TODO: check if there already is another config entry with this remote
            try:
                branch_result = subprocess.run(["git", "-C", subdir_path, "symbolic-ref", "--short", "-q", "HEAD"],
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                branch = branch_result.stdout.decode("utf-8").replace("\n", "")
                log.debug(f"  branch: {branch}")
                entry["git_tag"] = branch
            except subprocess.CalledProcessError:
                try:
                    tag_result = subprocess.run(["git", "-C", subdir_path, "describe", "--exact-match", "--tags"],
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    tag = tag_result.stdout.decode("utf-8").replace("\n", "")
                    log.debug(f"  tag: {tag}")
                    entry["git_tag"] = tag
                except subprocess.CalledProcessError:
                    log.warning(f"Skipping {name} because no branch or tag could be determined.")
                    continue
            new_config[name] = entry

        return new_config

    @classmethod
    def write_config(cls, new_config: dict, out_path: str):
        """Write the given config to the given path."""
        new_config_path = Path(out_path).expanduser().resolve()
        for config_entry_name, _ in new_config.items():
            log.info(f"Adding \"{Color.GREEN}{config_entry_name}{Color.CLEAR}\" to config.")
        with open(new_config_path, 'w', encoding='utf-8') as new_config_file:
            yaml.dump(new_config, new_config_file)
            log.info(f"Successfully saved config \"{new_config_path}\".")

    @classmethod
    def pull(cls, working_dir: Path, repos: list):
        """Pull all repos in working_dir or a restricted list of repos when provided."""
        pull_info = GitInfo.pull_all(working_dir, repos)
        pull_error_count = 0
        repo_count = 0
        for path, info in pull_info.items():
            if info["is_repo"]:
                repo_count += 1
                pulled = f"[{Color.GREEN}pulled{Color.CLEAR}]"
                if not info["pull_worked"]:
                    pulled = f"[{Color.RED}error during git-pull{Color.CLEAR}]"
                    pull_error_count += 1

                log.info(f"\"{Color.GREEN}{path.name}{Color.CLEAR}\"{pulled}")
            else:
                log.debug(f"\"{path.name}\" is not a git repository.")
        if pull_error_count > 0:
            log.info(f"{pull_error_count}/{repo_count} repositories could not be pulled.")

    @classmethod
    def scan_dependencies(cls, working_dir: Path, include_deps: list) -> dict:
        """Scan working_dir for dependencies."""
        log.info(f"Scanning \"{working_dir}\" for dependencies.")
        dependencies_files = list(working_dir.glob("**/dependencies.yaml")) + \
            list(working_dir.glob("**/dependencies.yml"))

        dependencies = {}
        for dependencies_file in dependencies_files:
            if dependencies_file.is_file():
                # filter _deps folders
                if not include_deps:
                    relative_path = dependencies_file.relative_to(working_dir).parent.as_posix()
                    if "_deps/" in relative_path:
                        log.info(
                            f"Ignoring dependencies in \"{dependencies_file}\" "
                            f"because this file is located in a \"_deps\" subdirectory.")
                        continue
                log.info(f"Parsing dependencies file: {dependencies_file}")
                with open(dependencies_file, encoding='utf-8') as dep:
                    try:
                        dependencies_yaml = yaml.safe_load(dep)
                        if dependencies_yaml is not None:
                            dependencies = {**dependencies, **dependencies_yaml}
                    except yaml.YAMLError as e:
                        log.error(f"Error parsing yaml of \"{dependencies_file}\": {e}")

        return dependencies

    @classmethod
    def parse_workspace_files(cls, workspace_files: list) -> dict:
        """Parse the given list of workspace_files and return a workspace dict when exactly one workspace file is in the list"""
        workspace = {}
        if len(workspace_files) == 1:
            workspace_file = Path(workspace_files[0]).expanduser().resolve()
            if workspace_file.is_file():
                log.info(f"Using workspace file: {workspace_file}")
                with open(workspace_file, encoding='utf-8') as wsp:
                    try:
                        workspace_yaml = yaml.safe_load(wsp)
                        if workspace_yaml is not None:
                            workspace = {**workspace, **workspace_yaml}
                    except yaml.YAMLError as e:
                        log.error(f"Error parsing yaml of {workspace_file}: {e}")
        return workspace

    @classmethod
    def checkout_local_dependencies(cls, workspace: dict, workspace_arg: str, dependencies: dict) -> list:
        """Checkout local dependencies in the workspace."""
        checkout = []
        if "local_dependencies" in workspace:
            workspace_dir = None
            # workspace given by command line always takes precedence
            if workspace_arg is not None:
                workspace_dir = Path(workspace_arg).expanduser().resolve()
                log.info(f"Using workspace directory \"{workspace_dir}\" from command line.")
            elif "workspace" in workspace:
                workspace_dir = Path(workspace["workspace"]).expanduser().resolve()
                log.info(f"Using workspace directory \"{workspace_dir}\" from workspace.yaml.")
            else:
                print("Cannot checkout requested dependencies without a workspace directory, stopping.")
                sys.exit(1)
            for name, entry in workspace["local_dependencies"].items():
                if name not in dependencies:
                    log.debug(f"{name}: listed in workspace.yaml, but not in dependencies. Ignoring.")
                    continue
                checkout_dir = workspace_dir / name
                git_tag = None
                if "git_tag" in dependencies[name]:
                    git_tag = dependencies[name]["git_tag"]
                if entry is not None and "git_tag" in entry:
                    git_tag = entry["git_tag"]
                checkout.append(checkout_local_dependency(name, dependencies[name]["git"], git_tag, checkout_dir, True))

        return checkout

    @classmethod
    def write_cmake(cls, workspace: dict, checkout: list, dependencies: dict, out_file: Path):
        """Generate a CMake file containing the dependencies in the given out_file."""
        templates_path = Path(__file__).parent / "templates"
        env = Environment(
            loader=FileSystemLoader(templates_path),
            trim_blocks=True,
        )
        env.filters['quote'] = quote

        cpm_template = env.get_template("cpm.jinja")
        render = cpm_template.render({
            "dependencies": dependencies,
            "checkout": checkout,
            "workspace": workspace})

        with open(out_file, 'w', encoding='utf-8') as out:
            log.info(f"Saving dependencies in: {out_file}")
            out.write(render)


def checkout_local_dependency(name: str, git: str, git_tag: str, checkout_dir: Path, keep_branch=False) -> dict:
    """
    Clone local dependency into checkout_dir.

    If the directory already exists only switch branches if the git repo is not dirty or keep_branch is True
    """
    def clone_dependency_repo(git: str, git_tag: str, checkout_dir: Path) -> None:
        """Clone given git repository at the given git_tag into checkout_dir."""
        git_clone_args = [git, checkout_dir]
        if git_tag:
            git_clone_args = ["--branch", git_tag, git, checkout_dir]
        else:
            log.debug("  No git-tag specified, cloning default branch.")
        git_clone_cmd = ["git", "clone"] + git_clone_args

        try:
            result = subprocess.run(git_clone_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            pretty_print_process(result, 4)
        except subprocess.CalledProcessError as e:
            error_message = f"   Error while cloning git repository during local dependency checkout: {str(e.stderr.decode())}"
            log.error(error_message)
            raise LocalDependencyCheckoutError(error_message) from e

    log.info(f"Setting up dependency \"{Color.GREEN}{name}{Color.CLEAR}\" in workspace")
    log.debug(f"  git-remote: \"{git}\"")
    log.debug(f"  git-tag: \"{git_tag}\"")
    log.debug(f"  local directory: \"{checkout_dir}\"")
    if checkout_dir.exists():
        log.debug(f"    ... the directory for dependency \"{name}\" already exists at \"{checkout_dir}\".")
        # check if git is dirty
        if GitInfo.is_dirty(checkout_dir):
            log.debug("    Repo is dirty, nothing will be done to this repo.")
        elif keep_branch:
            log.debug("    Keeping currently checked out branch.")
        else:
            # if the repo is clean we can safely switch branches
            if git_tag is not None:
                log.debug(f"    Repo is not dirty, checking out requested git tag \"{git_tag}\"")
                try:
                    result = subprocess.run(["git", "-C", checkout_dir, "checkout", git_tag],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    pretty_print_process(result, 4)
                except subprocess.CalledProcessError as result:
                    pretty_print_process(result, 4)
    else:
        clone_dependency_repo(git, git_tag, checkout_dir)

    return {"name": name, "path": checkout_dir, "git_tag": git_tag}


def parse_config(path: Path) -> dict:
    """Parse a config file in yaml format at the given path."""
    if path.is_file():
        with open(path, encoding='utf-8') as config_file:
            try:
                config_yaml = yaml.safe_load(config_file)
                if config_yaml is not None:
                    return config_yaml
            except yaml.YAMLError as e:
                print(f"Error parsing yaml of {config_file}: {e}")
    return {}


def setup_workspace(workspace_path: Path, config: dict, update=False) -> dict:
    """Setup a workspace at the given workspace_path using the given config."""
    log.info(f"Setting up workspace \"{workspace_path}\"")
    workspace_checkout = []
    for name, entry in config.items():
        checkout_dir = workspace_path / name
        git_tag = None
        if entry is not None and "git_tag" in entry:
            git_tag = entry["git_tag"]
        workspace_checkout.append(checkout_local_dependency(name, entry["git"], git_tag, checkout_dir))

    if len(workspace_checkout) > 0:
        log.info("Creating a workspace.yaml in each dependency directory, "
                 "ensuring that each repository uses the correct local dependency.")
    # create workspace.yaml files in these folders
    for entry in workspace_checkout:
        name = entry["name"]
        workspace_yaml_file = entry["path"] / "workspace.yaml"
        log.info(f"  {Color.GREEN}{name}{Color.CLEAR}")
        workspace_config = {}
        workspace_config["workspace"] = workspace_path.as_posix()
        workspace_config["local_dependencies"] = {}
        for workspace_entry in workspace_checkout:
            workspace_config_entry = {}
            workspace_config_entry["git_tag"] = workspace_entry["git_tag"]
            workspace_config["local_dependencies"][workspace_entry["name"]] = workspace_config_entry
        if workspace_yaml_file.exists():
            log.warning(f"    \"{workspace_yaml_file}\" already exists.")
            if update:
                log.info("    Updating workspace.yaml")
            else:
                log.warning("    Use --update to overwrite workspace.yaml")
                continue
        log.debug(f"    Writing \"{workspace_yaml_file}\"")
        with open(workspace_yaml_file, 'w', encoding='utf-8') as w:
            yaml.dump(workspace_config, w)
    log.info("Done.")
    return workspace_checkout


def create_vscode_workspace(workspace_path: Path, workspace_checkout: dict):
    """Create a VS Code compatible workspace file at the given workspace_path."""
    vscode_workspace_file_path = workspace_path / f"{workspace_path.name}.code-workspace"

    content = {}
    if vscode_workspace_file_path.exists():
        log.warning(
            f"VS Code workspace file \"{vscode_workspace_file_path}\" exists.")
        log.info("Updating VS Code workspace file.")
        with open(vscode_workspace_file_path, 'r', encoding='utf-8') as ws_file:
            content = json.load(ws_file)
    else:
        log.info(f"Creating VS Code workspace file at: {vscode_workspace_file_path}")
    if "folders" not in content:
        content["folders"] = []
    for entry in workspace_checkout:
        folder = entry["path"].name
        if not any(f["path"] == folder for f in content["folders"]):
            log.debug(f"Dependency \"{Color.GREEN}{folder}{Color.GREY}\" added to VS Code workspace file")
            content["folders"].append({"path": folder})
    with open(vscode_workspace_file_path, 'w', encoding='utf-8') as ws_file:
        json.dump(content, ws_file, indent="\t")


def get_parser() -> argparse.ArgumentParser:
    """Return the argument parser containign all command line options."""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description="Everest Dependency Manager")
    parser.add_argument('--version', action='version', version='%(prog)s 0.2.0')
    parser.add_argument(
        "--workspace", metavar='WORKSPACE',
        help="Directory in which source code repositories that are explicity requested are checked out.",
        required=False)
    parser.add_argument("--working_dir", metavar='WORKINGDIR', default=".",
                        help="Working directory, default is the current one.", required=False)
    parser.add_argument("--out", metavar='OUTFILENAME', default="dependencies.cmake",
                        help="Path of the file that will contain the generated CPM cmake information")
    parser.add_argument(
        "--include_deps", action='store_true',
        help="Include dependency files that are stored in \"_deps\" directories. "
             "Given that files in these directories are part of the in-tree source cache of CPM "
             "you probably almost never want to do this.")
    parser.add_argument(
        "--config", metavar='CONFIG',
        help="Path to a config file that contains the repositories that should be checked out into the workspace.",
        required=False)
    parser.add_argument(
        "--create-vscode-workspace", action="store_true",
        help="Create a VS Code workspace by saving a <workspace>.code-workspace file in the workspace folder.")
    parser.add_argument(
        "--update", action="store_true",
        help="Update workspace.yaml files with autogenerated ones.")
    parser.add_argument(
        "--cmake", action="store_true",
        help="Use this flag to indicate that the dependency manager was called from a CMake script.")
    parser.add_argument(
        "--verbose", action="store_true",
        help="Verbose output.")
    parser.add_argument(
        "--nocolor", action="store_true",
        help="No color output.")
    parser.add_argument(
        "--register-cmake-module", action="store_true",
        help="Setup the CMake registry entry for EDM.")
    parser.add_argument(
        "--install-bash-completion", action="store_true",
        help="Install bash completion if possible.")
    parser.add_argument(
        "--create-config", metavar='CREATECONFIG',
        help="Creates a config file at the given path containing all dependencies from the working directory.",
        required=False)
    parser.add_argument(
        "--external-in-config", action="store_true",
        help="Include external dependencies in created config file.")
    parser.add_argument(
        "--include-remotes", metavar='INTERNAL',
        help="List of git remotes that are included in a created config file",
        nargs="*",
        default=["git@github.com:EVerest/*"],
        required=False)
    parser.add_argument(
        "--git-info", action="store_true",
        help="Show information of git repositories in working_dir")
    parser.add_argument(
        "--git-fetch", action="store_true",
        help="Use git-fetch to get updated info from remote")
    parser.add_argument(
        "--git-pull",
        help="Use git-pull to pull all git repositories in working_dir",
        nargs="*",
        required=False)
    # TODO(kai): consider implementing interactive mode
    # parser.add_argument("--interactive", action='store_true',
    #                     help="Interactively ask which repositories should be checked out.")

    return parser


def setup_logging(verbose: bool, nocolor: bool):
    """Setup logging, choosing logger level and if colorful log output is requested."""
    if verbose:
        log.setLevel(level=logging.DEBUG)
    else:
        log.setLevel(level=logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter(color=not nocolor))
    log.addHandler(console_handler)

    if not nocolor:
        log.debug(
            "Using \033[1;31mc\033[1;33mo\033[93ml\033[92mo\033[94mr\033[34mf\033[95mu\033[35ml\033[0m \033[1m"
            "output\033[0m")


def main(parser: argparse.ArgumentParser):
    """The main entrypoint of edm. Provides different functionality based on the given command line arguments."""
    args = parser.parse_args()

    setup_logging(args.verbose, args.nocolor)

    working_dir = Path(args.working_dir).expanduser().resolve()

    if not os.environ.get("CPM_SOURCE_CACHE"):
        log.warning("CPM_SOURCE_CACHE environment variable is not set, this might lead to unintended behavior.")

    if args.register_cmake_module:
        log.info("Registering EDM CMake module in CMake registry")
        install_cmake()

    if args.install_bash_completion:
        install_bash_completion()
        sys.exit(0)

    if args.git_pull is not None:
        EDM.pull(working_dir, repos=args.git_pull)
        sys.exit(0)

    if args.git_info:
        EDM.show_git_info(working_dir, args.workspace, args.git_fetch)
        sys.exit(0)

    if not args.config and not args.cmake and not args.create_config:
        if args.update:
            if not args.workspace:
                args.workspace = Path(".").expanduser().resolve()
                log.info(f"No workspace provided, using current directory "
                         f"\"{args.workspace}\"")
            config_path = Path(args.workspace) / "workspace-config.yaml"
            args.config = config_path.expanduser().resolve()
            log.info(f"No config provided, using \"{args.config}\"")
        else:
            log.info("No --config, --cmake or --create-config parameter given, exiting.")
            sys.exit(0)

    if args.config:
        if not args.workspace:
            log.error("A workspace path must be provided if supplying a config. Stopping.")
            sys.exit(1)

        EDM.setup_workspace_from_config(args.workspace, args.config, args.update, args.create_vscode_workspace)
        sys.exit(0)

    if not args.cmake and not args.create_config:
        log.error("FIXME")
        sys.exit(1)

    out_file = Path(args.out).expanduser().resolve()

    workspace_files = list(working_dir.glob("workspace.yaml")) + list(working_dir.glob("workspace.yml"))
    if len(workspace_files) > 1:
        log.error(
            f"There are multiple workspace files ({workspace_files}) only one file is allowed per repository!")
        sys.exit(1)

    dependencies = EDM.scan_dependencies(working_dir, args.include_deps)

    if args.create_config:
        log.info("Creating config")
        new_config = EDM.config_from_dependencies(dependencies, args.external_in_config, args.include_remotes)
        new_config = EDM.create_config(working_dir, new_config, args.external_in_config, args.include_remotes)
        EDM.write_config(new_config, args.create_config)
        sys.exit(0)

    if not args.cmake:
        log.error("Calling the dependency manager without the --config parameter indicates usage from a CMake script. "
                  "If this is intendend , please use the --cmake flag to explicitly request this functionality.")
        sys.exit(1)

    workspace = EDM.parse_workspace_files(workspace_files)
    checkout = EDM.checkout_local_dependencies(workspace, args.workspace, dependencies)
    EDM.write_cmake(workspace, checkout, dependencies, out_file)


if __name__ == "__main__":
    parser = get_parser()
    main(parser)
