#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 - 2022 Pionix GmbH and Contributors to EVerest
#
"""Everest Dependency Manager."""
from edm_tool import edm
__version__ = "0.5.0"


def get_parser():
    """Return the command line parser."""
    return edm.get_parser(__version__)


def main():
    """Main entrypoint of edm."""
    edm.main(get_parser())
