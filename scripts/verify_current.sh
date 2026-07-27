#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/verify_checkpoint.py \
  current/macro_cegis_30.json \
  current/macro_cegis_30_5.colors \
  --checkpoint current/macro_cegis_30_checkpoint.json
printf '\nFor the full 3.2M-edge geometry pass, add --geometry.\n'
