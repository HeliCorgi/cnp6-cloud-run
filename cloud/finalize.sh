#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BUILD="$ROOT/cloud_download/build"
OUT="$ROOT/cloud_out/final"
mkdir -p "$OUT"
cp -a "$BUILD"/. "$OUT"/

TABU="$(find "$ROOT/cloud_download/colors" -type f -name 'core31_*.tabu' -print -quit 2>/dev/null || true)"
if [[ -n "$TABU" ]]; then
  python3 current/extend_core_solution.py "$OUT/macro_cegis_31.json" \
    "$OUT/macro_cegis_31_core5.json" "$OUT/core31.seed" "$TABU" \
    "$OUT/macro_cegis_31_5.colors"
  python3 scripts/verify_checkpoint.py "$OUT/macro_cegis_31.json" "$OUT/macro_cegis_31_5.colors"
  cat > "$OUT/RESULT.txt" <<'RESULT'
5-SAT: step31 has a verified 5-coloring.
This is not a proof of chi(R^2) >= 6. Continue from this checkpoint.
RESULT
else
  cat > "$OUT/RESULT.txt" <<'RESULT'
UNKNOWN: the configured TabuCol portfolio did not find a 5-coloring.
This is NOT an UNSAT result and NOT a proof of chi(R^2) >= 6.
Preserve this package for a larger portfolio or exact SAT solving.
RESULT
fi
(
  cd "$OUT"
  zip -q -r "$ROOT/CNP6_STEP31_RESULT.zip" .
)
cat "$OUT/RESULT.txt"
