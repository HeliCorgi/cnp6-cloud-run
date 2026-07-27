# Next experiment: step 30 to step 31

## Purpose

Test whether a broader, color-permutation-distinct model library reduces the repeated finite-library overfitting observed through step 30.

## Input

- `current/macro_cegis_30.json`
- `current/macro_cegis_30_core5.json`
- `current/macro_cegis_30_5.colors`
- first 16 graph vertices as the macro template

## Default parameters

```text
MODELS=50
MODEL_RESTARTS=24
MODEL_ITERS=50,000,000
SCAN_SEEDS=10
CANDIDATES_PER_SEED=500
SELECT_COUNT=100
COLOR_RESTARTS=96
COLOR_ITERS=200,000,000
```

## Command

```bash
tmux new -s cnp6
bash scripts/resume_step31.sh 2>&1 | tee logs/step31-console.log
```

## Stage outputs

```text
work/step31/models.lst
work/step31/candidates/all.txt
work/step31/eval/all.txt
work/step31/selected.lines
work/step31/macro_cegis_31.json
work/step31/macro_cegis_31_core5.json
work/step31/macro_cegis_31_5.colors       # only if found
work/step31/STATUS.txt
step31_checkpoint.zip
```

## Decision rules

### A verified 5-coloring is found

- mark step 31 as 5-SAT;
- preserve graph and coloring hashes;
- generate a new diverse model pool on step 31;
- continue CEGIS.

### TabuCol does not find a coloring

Mark `UNKNOWN`. Then:

1. encode the reduced core as a one-hot 5-coloring CNF;
2. add color symmetry breaking on a fixed small subgraph;
3. run at least two independent exact SAT solvers;
4. if UNSAT, produce and verify DRAT/LRAT;
5. only then start exact-coordinate reconstruction.

### Too few common killers are found

Increase model diversity before increasing the candidate count. A low kill-all rate may mean the model pool is finally covering genuinely different coloring regions.

## Pre-registered measurements

Record:

- number of unique models after color canonicalization;
- pairwise aligned Hamming-distance distribution;
- candidates generated per geometric scan seed;
- number and fraction killing all models;
- selected support-union size;
- new vertices and edges;
- reduced core size;
- TabuCol best conflict trajectory and time;
- exact hashes of graph and coloring.

## Stop conditions

Stop and inspect rather than blindly growing the graph when one occurs:

- graph JSON materialization exceeds practical local storage/time;
- kill-all candidates become extremely rare;
- independent model generation repeatedly returns the same canonical models;
- TabuCol remains unresolved after a predeclared portfolio budget;
- geometry tolerance begins accumulating beyond the current threshold.
