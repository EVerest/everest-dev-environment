#!/usr/bin/env python3
import yaml
from argparse import ArgumentParser
from pathlib import Path
import sys

def generate_deps(args):
    deps = yaml.safe_load(open(args.dependencies_yaml, 'r'))
    print("Buid files: ", args.build_file, file=sys.stderr)
    if args.build_file:
        build_files = dict((f.split(":")[1], f) for f in args.build_file)
    else:
        build_files = {}

    print('load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")')
    print('load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")')
    print()
    print()

    print("def edm_deps():")

    for name, desc in deps.items():
        repo = desc['git']
        tag = desc["git_tag"]
        commit = "None"

        # Check that tag is hexadecimal 40-character string
        if len(tag) == 40 and all(c in "0123456789abcdef" for c in tag.lower()):
            tag, commit = "None", f'"{tag}"'
        else:
            tag, commit = f'"{tag}"', "None"
        
        build_file_name = f"BUILD.{name}.bazel"
        if build_file_name in build_files:
            build_file_label = build_files[build_file_name]
            build_file = f'"{build_file_label}"'
        else:
            build_file = "None"

        print(
            f"""
    maybe(
        git_repository,
        name = "{name}",
        remote = "{repo}",
        tag = {tag},
        commit = {commit},
        build_file = {build_file},
    )
"""
        )
