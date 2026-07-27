#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SHARD="${1:?shard number required}"
MODE="${2:-normal}"
SEED_OFFSET="${3:-0}"
BUILD="$ROOT/cloud_download/build"
OUT="$ROOT/cloud_out/color_${SHARD}"
BIN="$ROOT/cloud_out/bin"
mkdir -p "$OUT" "$BIN"

g++ -O3 -std=c++17 -pthread current/tabucol_seed.cpp -o "$BIN/tabucol_seed"
case "$MODE" in
  quick)  RESTARTS=8;  ITERS=25000000 ;;
  normal) RESTARTS=24; ITERS=100000000 ;;
  full)   RESTARTS=48; ITERS=250000000 ;;
  *) echo "unknown mode: $MODE" >&2; exit 2 ;;
esac
seed=$((9200000 + SEED_OFFSET*100000 + SHARD*1000))
set +e
timeout 310m "$BIN/tabucol_seed" "$BUILD/macro_cegis_31_core5.json" 5 \
  "$RESTARTS" "$ITERS" "$seed" "$BUILD/core31.seed" "$OUT/core31_${SHARD}.tabu"
rc=$?
set -e
if [[ $rc -eq 0 ]]; then
  echo SAT > "$OUT/STATUS.txt"
else
  rm -f "$OUT/core31_${SHARD}.tabu"
  echo "UNKNOWN rc=$rc" > "$OUT/STATUS.txt"
fi
exit 0
