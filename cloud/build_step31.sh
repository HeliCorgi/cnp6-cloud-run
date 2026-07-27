#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MODE="${1:-normal}"
SELECT_COUNT="${2:-100}"
OUT="$ROOT/cloud_out/build"
BIN="$ROOT/cloud_out/bin"
mkdir -p "$OUT/models" "$OUT/input" "$BIN"

# Base verified model is always retained.
cp current/macro_cegis_30_5.colors "$OUT/models/base.colors"

# Collect all generated full colorings and deduplicate under global color permutation.
declare -A seen
base_hash="$(python3 scripts/canonicalize_coloring.py "$OUT/models/base.colors")"
seen["$base_hash"]=1
: > "$OUT/models.lst"
echo "$OUT/models/base.colors" >> "$OUT/models.lst"
while IFS= read -r -d '' f; do
  h="$(python3 scripts/canonicalize_coloring.py "$f")"
  if [[ -z "${seen[$h]+x}" ]]; then
    seen["$h"]=1
    dst="$OUT/models/model_$(printf '%03d' $(wc -l < "$OUT/models.lst")).colors"
    cp "$f" "$dst"
    echo "$dst" >> "$OUT/models.lst"
  fi
done < <(find "$ROOT/cloud_download/models" -type f -name '*.colors' -print0 2>/dev/null || true)

echo "retained models=$(wc -l < "$OUT/models.lst")"

# Combine candidate shards.
find "$ROOT/cloud_download/scans" -type f -name 'candidates_*.txt' -print0 2>/dev/null \
  | sort -z | xargs -0 -r cat > "$OUT/candidates.txt"
CANDS=$(wc -l < "$OUT/candidates.txt")
echo "candidate lines=$CANDS"
if [[ "$CANDS" -eq 0 ]]; then
  echo "NO_CANDIDATES" > "$OUT/STATUS.txt"
  exit 20
fi

python3 scripts/prepare_scanner_inputs.py current/macro_cegis_30.json \
  current/macro_cegis_30_core5.json "$OUT/input"
g++ -O3 -std=c++17 current/multi_eval.cpp -o "$BIN/multi_eval"
"$BIN/multi_eval" "$OUT/input/graph.coords" "$OUT/input/macro16.coords" \
  "$OUT/input/fixedmask.txt" "$OUT/models.lst" "$OUT/candidates.txt" "$OUT/eval.txt"

python3 scripts/select_common_killers.py "$OUT/eval.txt" --count "$SELECT_COUNT" --output "$OUT/selected.lines"
SELECTED=$(grep -cve '^$' "$OUT/selected.lines" || true)
echo "selected=$SELECTED"
if [[ "$SELECTED" -eq 0 ]]; then
  echo "NO_COMMON_KILLERS" > "$OUT/STATUS.txt"
  exit 21
fi

python3 current/add_robust_batch_fast.py current/macro_cegis_30.json "$OUT/candidates.txt" \
  "$OUT/selected.lines" "$OUT/macro_cegis_31.json.tmp"
mv "$OUT/macro_cegis_31.json.tmp" "$OUT/macro_cegis_31.json"
python3 current/reduce_graph.py "$OUT/macro_cegis_31.json" "$OUT/macro_cegis_31_core5.json.tmp"
mv "$OUT/macro_cegis_31_core5.json.tmp" "$OUT/macro_cegis_31_core5.json"
python3 current/make_core_seed.py current/macro_cegis_30.json current/macro_cegis_30_5.colors \
  "$OUT/macro_cegis_31_core5.json" "$OUT/core31.seed"
cat > "$OUT/STATUS.txt" <<STATUS
BUILT
models=$(wc -l < "$OUT/models.lst")
candidates=$CANDS
selected=$SELECTED
STATUS
