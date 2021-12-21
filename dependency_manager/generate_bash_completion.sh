#!/bin/bash
##
## SPDX-License-Identifier: Apache-2.0
##
## Copyright 2020 - 2021 Pionix GmbH and Contributors to EVerest
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
echo "generating bash-completion file"
SRC_DIR="$(dirname "${BASH_SOURCE[0]}")/src"
echo "Using module found in ${SRC_DIR}"
cd "${SRC_DIR}"
BASH_COMPLETION_FILE_DIR="$(pwd)"
BASH_COMPLETION_FILE="${BASH_COMPLETION_FILE_DIR}/edm_tool/edm-completion.bash"
shtab --shell=bash -u edm_tool.get_parser --prog edm > "${BASH_COMPLETION_FILE}"