# Continuation prompt for another research/coding agent

Use this prompt together with the complete handoff folder.

---

You are continuing a computational search for a finite non-5-colorable unit-distance graph. Read `README_FIRST.md`, `docs/HANDOFF_FULL.md`, `docs/KNOWN_LIMITS.md`, and verify `MANIFEST.sha256` before doing anything.

The current durable checkpoint is step 30:

- graph: `current/macro_cegis_30.json`
- vertices: 68,802
- edges: 3,216,000
- verified 5-coloring: `current/macro_cegis_30_5.colors`
- reduced core: `current/macro_cegis_30_core5.json`
- graph SHA-256: `32ba5afa55e88eee5d21821a64526b0704a46496915d8ed8c7f7639c86b0ce98`
- coloring SHA-256: `1abc6088fd5c152b3a2497d24e2c1803a4894fdc266dcd7f7fec50a4ff86ca4e`

First run:

```bash
bash scripts/verify_current.sh
```

Then continue from step 30 using the staged pipeline:

```bash
bash scripts/resume_step31.sh
```

The intended experiment is to generate at least 50 global-color-permutation-distinct step-30 colorings, generate randomized core-robust template placements, retain candidates that kill every stored model, choose support-diverse candidates, build step 31, reduce it, and search for a verified 5-coloring.

Critical rules:

1. A timeout or failed heuristic search is `UNKNOWN`, not `UNSAT`.
2. Never claim a chi>=6 proof from floating coordinates or heuristic non-colorability.
3. Every found coloring must be checked on every edge.
4. Every graph write must be atomic and hashed.
5. Preserve stage outputs and logs so interrupted runs can resume.
6. If a candidate appears 5-UNSAT, switch to an exact SAT solver with a checkable proof certificate and independently reconstruct exact unit-distance coordinates.
7. Do not repeat the previously identified errors: wrong index space, nonminimal raw cores, low-degree recoloring escape, or incorrect restoration ordering.

Report concrete artifacts and hashes, not only narrative summaries.
