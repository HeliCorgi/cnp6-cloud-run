#!/usr/bin/env bash
# Resumable step30 -> step31 macro CEGIS pipeline.
# Run inside WSL2/Linux. Every expensive stage writes its own checkpoint.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODELS="${MODELS:-50}"
MODEL_RESTARTS="${MODEL_RESTARTS:-24}"
MODEL_ITERS="${MODEL_ITERS:-50000000}"
SCAN_SEEDS="${SCAN_SEEDS:-10}"
CANDIDATES_PER_SEED="${CANDIDATES_PER_SEED:-500}"
SELECT_COUNT="${SELECT_COUNT:-100}"
COLOR_RESTARTS="${COLOR_RESTARTS:-96}"
COLOR_ITERS="${COLOR_ITERS:-200000000}"
THREADS="${THREADS:-$(nproc)}"

CUR="$ROOT/current"
W="$ROOT/work/step31"
BIN="$ROOT/work/bin"
LOG="$ROOT/logs"
mkdir -p "$W" "$BIN" "$LOG" "$W/models" "$W/candidates" "$W/eval"
exec > >(tee -a "$LOG/step31.log") 2>&1

echo "=== step31 resume $(date -Is) ==="
echo "MODELS=$MODELS SCAN_SEEDS=$SCAN_SEEDS CANDIDATES_PER_SEED=$CANDIDATES_PER_SEED SELECT_COUNT=$SELECT_COUNT"

stage() { echo; echo "[$(date -Is)] $*"; }

stage "verify step30"
python3 scripts/verify_checkpoint.py "$CUR/macro_cegis_30.json" "$CUR/macro_cegis_30_5.colors" \
  --checkpoint "$CUR/macro_cegis_30_checkpoint.json"

stage "compile GNU C++ tools"
g++ -O3 -std=c++17 -pthread "$CUR/tabucol_seed.cpp" -o "$BIN/tabucol_seed"
g++ -O3 -std=c++17 "$CUR/core_robust_scan_shuf.cpp" -o "$BIN/core_robust_scan_shuf"
g++ -O3 -std=c++17 "$CUR/multi_eval.cpp" -o "$BIN/multi_eval"

if [[ ! -f "$W/inputs.done" ]]; then
  stage "prepare scanner inputs"
  python3 scripts/prepare_scanner_inputs.py "$CUR/macro_cegis_30.json" "$CUR/macro_cegis_30_core5.json" "$W/input"
  touch "$W/inputs.done"
fi

if [[ ! -f "$W/models.done" ]]; then
  stage "generate color-permutation-distinct step30 models"
  cp "$CUR/macro_cegis_30_5.colors" "$W/models/model_000.colors"
  python3 scripts/canonicalize_coloring.py "$W/models/model_000.colors" > "$W/models/hashes.txt"
  printf '%s\n' "$W/models/model_000.colors" > "$W/models.lst"
  accepted=1
  attempt=1
  max_attempts=$(( MODELS * 8 ))
  while (( accepted < MODELS && attempt <= max_attempts )); do
    printf 'model attempt %d accepted %d/%d\n' "$attempt" "$accepted" "$MODELS"
    tabu="$W/models/attempt_${attempt}.tabu"
    colors="$W/models/attempt_${attempt}.colors"
    if "$BIN/tabucol_seed" "$CUR/macro_cegis_30_core5.json" 5 "$MODEL_RESTARTS" "$MODEL_ITERS" \
         "$((910000 + attempt))" "$CUR/core30.seed" "$tabu"; then
      python3 "$CUR/extend_core_solution.py" "$CUR/macro_cegis_30.json" "$CUR/macro_cegis_30_core5.json" \
        "$CUR/core30.seed" "$tabu" "$colors"
      h="$(python3 scripts/canonicalize_coloring.py "$colors")"
      if ! grep -qx "$h" "$W/models/hashes.txt"; then
        echo "$h" >> "$W/models/hashes.txt"
        echo "$colors" >> "$W/models.lst"
        accepted=$((accepted+1))
      else
        rm -f "$colors"
      fi
    fi
    attempt=$((attempt+1))
  done
  actual="$(wc -l < "$W/models.lst")"
  echo "model pool size=$actual"
  if (( actual < 2 )); then
    echo "ERROR: no diverse model pool" >&2; exit 3
  fi
  touch "$W/models.done"
fi

if [[ ! -f "$W/candidates.done" ]]; then
  stage "scan core-robust candidate placements"
  : > "$W/candidates/all.txt"
  for s in $(seq 1 "$SCAN_SEEDS"); do
    out="$W/candidates/seed_${s}.txt"
    if [[ ! -s "$out" ]]; then
      "$BIN/core_robust_scan_shuf" \
        "$W/input/graph.coords" "$W/input/macro16.coords" "$CUR/macro_cegis_30_5.colors" \
        "$W/input/fixedmask.txt" "$out" "$CANDIDATES_PER_SEED" "$((310000+s))" || true
    fi
    cat "$out" >> "$W/candidates/all.txt"
  done
  echo "candidate lines=$(wc -l < "$W/candidates/all.txt")"
  touch "$W/candidates.done"
fi

if [[ ! -f "$W/eval.done" ]]; then
  stage "evaluate candidates against every retained model"
  "$BIN/multi_eval" "$W/input/graph.coords" "$W/input/macro16.coords" "$W/input/fixedmask.txt" \
      "$W/models.lst" "$W/candidates/all.txt" "$W/eval/all.txt"
  touch "$W/eval.done"
fi

if [[ ! -f "$W/selected.done" ]]; then
  stage "select support-diverse common killers"
  python3 scripts/select_common_killers.py "$W/eval/all.txt" --count "$SELECT_COUNT" --output "$W/selected.lines"
  touch "$W/selected.done"
fi

if [[ ! -f "$W/graph.done" ]]; then
  stage "construct step31 graph atomically"
  tmp="$W/macro_cegis_31.json.tmp"
  python3 "$CUR/add_robust_batch_fast.py" "$CUR/macro_cegis_30.json" "$W/candidates/all.txt" \
      "$W/selected.lines" "$tmp"
  mv "$tmp" "$W/macro_cegis_31.json"
  touch "$W/graph.done"
fi

if [[ ! -f "$W/core.done" ]]; then
  stage "reduce step31 to 5-core plus domination reductions"
  tmp="$W/macro_cegis_31_core5.json.tmp"
  python3 "$CUR/reduce_graph.py" "$W/macro_cegis_31.json" "$tmp"
  mv "$tmp" "$W/macro_cegis_31_core5.json"
  python3 "$CUR/make_core_seed.py" "$CUR/macro_cegis_30.json" "$CUR/macro_cegis_30_5.colors" \
      "$W/macro_cegis_31_core5.json" "$W/core31.seed"
  touch "$W/core.done"
fi

if [[ ! -f "$W/color.done" ]]; then
  stage "search for a step31 5-coloring"
  set +e
  "$BIN/tabucol_seed" "$W/macro_cegis_31_core5.json" 5 "$COLOR_RESTARTS" "$COLOR_ITERS" \
      311031 "$W/core31.seed" "$W/core31.tabu"
  rc=$?
  set -e
  if [[ $rc -ne 0 ]]; then
    cat > "$W/STATUS.txt" <<EOF
UNKNOWN: TabuCol did not find a 5-coloring within the configured budget.
This is not an UNSAT result. Preserve this directory and use an exact SAT solver or a larger portfolio.
EOF
    echo "step31 remains UNKNOWN; no chi>=6 claim" >&2
    exit 10
  fi
  python3 "$CUR/extend_core_solution.py" "$W/macro_cegis_31.json" "$W/macro_cegis_31_core5.json" \
      "$W/core31.seed" "$W/core31.tabu" "$W/macro_cegis_31_5.colors"
  python3 scripts/verify_checkpoint.py "$W/macro_cegis_31.json" "$W/macro_cegis_31_5.colors"
  echo "5-SAT: step31 has a verified 5-coloring" > "$W/STATUS.txt"
  touch "$W/color.done"
fi

stage "make continuation archive"
(
  cd "$W"
  zip -q -r "$ROOT/step31_checkpoint.zip" .
)
echo "DONE: $ROOT/step31_checkpoint.zip"
