#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update
sudo apt-get install -y build-essential python3 python3-venv jq tmux zip unzip time
printf '\nInstalled: g++, Python, jq, tmux, zip.\n'
printf 'Optional SAT solvers should be installed separately and their versions recorded.\n'
