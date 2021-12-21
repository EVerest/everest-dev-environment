#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 - 2021 Pionix GmbH and Contributors to EVerest
#
from edm_tool import edm


def get_parser():
    return edm.get_parser()


def main():
    edm.main(get_parser())
