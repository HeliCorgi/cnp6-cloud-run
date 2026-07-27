#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SHARD="${1:?shard number required}"
MODE="${2:-normal}"
SEED_OFFSET="${3:-0}"
OUT="$ROOT/cloud_out/models_${SHARD}"
BIN="$ROOT/cloud_out/bin"
mkdir -p "$OUT" "$BIN"

g++ -O3 -std=c++17 -pthread current/tabucol_seed.cpp -o "$BIN/tabucol_seed"
case "$MODE" in
  quick)  ATTEMPTS=2; RESTARTS=4;  ITERS=5000000 ;;
  normal) ATTEMPTS=5; RESTARTS=10; ITERS=25000000 ;;
  full)   ATTEMPTS=8; RESTARTS=20; ITERS=75000000 ;;
  *) echo "unknown mode: $MODE" >&2; exit 2 ;;
esac

: > "$OUT/hashes.txt"
for a in $(seq 0 $((ATTEMPTS-1))); do
  seed=$((7000000 + SEED_OFFSET*100000 + SHARD*1000 + a))
  tabu="$OUT/model_${SHARD}_${a}.tabu"
  colors="$OUT/model_${SHARD}_${a}.colors"
  echo "model shard=$SHARD attempt=$a seed=$seed"
  set +e
  timeout 50m "$BIN/tabucol_seed" current/macro_cegis_30_core5.json 5 "$RESTARTS" "$ITERS" \
    "$seed" current/core30.seed "$tabu"
  rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    python3 current/extend_core_solution.py current/macro_cegis_30.json \
      current/macro_cegis_30_core5.json current/core30.seed "$tabu" "$colors"
    h="$(python3 scripts/canonicalize_coloring.py "$colors")"
    if grep -qx "$h" "$OUT/hashes.txt"; then
      rm -f "$colors" "$tabu" "${colors%.colors}_certificate.json"
    else
      echo "$h" >> "$OUT/hashes.txt"
    fi
  else
    echo "attempt $a did not find a coloring (rc=$rc); continuing"
    rm -f "$tabu" "$colors"
  fi
done
ls -lh "$OUT" || true
