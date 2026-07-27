#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SHARD="${1:?shard number required}"
MODE="${2:-normal}"
SEED_OFFSET="${3:-0}"
OUT="$ROOT/cloud_out/scan_${SHARD}"
BIN="$ROOT/cloud_out/bin"
mkdir -p "$OUT" "$BIN" "$ROOT/cloud_out/input"

g++ -O3 -std=c++17 current/core_robust_scan_shuf.cpp -o "$BIN/core_robust_scan_shuf"
python3 scripts/prepare_scanner_inputs.py current/macro_cegis_30.json \
  current/macro_cegis_30_core5.json "$ROOT/cloud_out/input"
case "$MODE" in
  quick)  LIMIT=100 ;;
  normal) LIMIT=300 ;;
  full)   LIMIT=600 ;;
  *) echo "unknown mode: $MODE" >&2; exit 2 ;;
esac
seed=$((8100000 + SEED_OFFSET*100000 + SHARD))
outfile="$OUT/candidates_${SHARD}.txt"
set +e
timeout 5h10m "$BIN/core_robust_scan_shuf" \
  "$ROOT/cloud_out/input/graph.coords" "$ROOT/cloud_out/input/macro16.coords" \
  current/macro_cegis_30_5.colors "$ROOT/cloud_out/input/fixedmask.txt" \
  "$outfile" "$LIMIT" "$seed"
rc=$?
set -e
[[ -f "$outfile" ]] || : > "$outfile"
echo "scan rc=$rc lines=$(wc -l < "$outfile")"
exit 0
