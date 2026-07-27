# Known limits and claims policy

## No current six-color lower-bound proof

The latest macro candidate, step 30, is 5-colorable. Its verified coloring is included. None of the current artifacts proves

\[
\chi(\mathbb R^2)\ge 6.
\]

## `UNKNOWN` is not `UNSAT`

A timeout, TabuCol failure, Z3 `unknown`, a high residual conflict count, or a hard 42-case split is not a proof of non-5-colorability.

A valid computational lower-bound result would require at least:

1. a finite graph whose edges are exactly unit distances in a certified coordinate field;
2. a complete 5-UNSAT proof from an exact solver;
3. an independently checkable proof certificate, preferably DRAT/LRAT or equivalent;
4. an independent graph and geometry verifier.

## Floating geometry

The macro campaign uses floating coordinates and registers edges within a tolerance. At step 30, the largest registered-edge length error is approximately

\[
2.9993509054\times 10^{-7}.
\]

This is adequate for exploratory graph generation, not for a final mathematical proof. Any future 5-UNSAT candidate must be reconstructed in exact algebraic coordinates and re-enumerated exactly.

## Finite-model overfitting

Repeatedly, a set of placements killed every stored 5-coloring but a new 5-coloring appeared after rebuilding the graph. “Kills all current models” is a CEGIS step, not a theorem.

## Semantic interface scope

The distributed-interpolant experiments concern specified equality-observation languages over A/B CNFs. Negative results do not rule out arbitrary semantic interfaces or other predicates.

## Session-only results without persisted certificates

During the computational session, a 13-observation semantic separator and a 19-edge Moser-spindle-like conditional core were reported after a corrected index interpretation. The corrected observation list and machine-readable certificate are **not present in the available files**. Treat this as a lead requiring recomputation, not as a frozen theorem.

## Model manifests in the step 30 checkpoint

`current/models*/manifest.json` records earlier model hashes and original temporary paths, but the corresponding model color files are not all included. The continuation pipeline regenerates a fresh model pool on step 30.

## Proof language

Use these phrases:

- “verified 5-coloring” when every edge was checked;
- “candidate” for an unproved graph;
- “UNKNOWN” for a solver timeout;
- “conditional forcing lemma” when external equality conditions are present.

Do not use “proof of \(\chi\ge6\)” until the exact geometry and 5-UNSAT certificate both exist.
