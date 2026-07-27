# Full CNP6 research handoff

**Date:** 2026-07-27  
**Primary target:** construct and certify a finite unit-distance graph that is not 5-colorable, thereby proving \(\chi(\mathbb R^2)\ge6\).  
**Current result:** target not reached. Latest macro candidate step 30 is verified 5-colorable.

---

## 1. Artifact provenance

This package deliberately separates three levels of evidence.

### Level A — source-backed original research snapshot

`upstream/cnp6_original_snapshot.zip` is the uploaded repository snapshot. It contains the G510/K2 data, P2 conditional lemma artifacts, multicore data, k=4 certificate material, ROT_T4 work, phi-forge work, and generation/verification scripts.

### Level B — session-generated machine-readable artifacts

These are available and can be rerun locally:

- `semantic/A.cnf`, `semantic/B.cnf`
- `semantic/distforge_pairs.npz`
- distributed CEGIS scripts and traces
- `current/macro_cegis_30.json`
- `current/macro_cegis_30_5.colors`
- step 30 5-core, seed, TabuCol output and verifier scripts
- candidate pools/evaluation files from steps 27–30

### Level C — session observations not fully frozen

A corrected 13-observation semantic separator and a 19-edge conditional core were reported during the interactive session. The corrected vertex list and proof files were not preserved in the available upload. They must be recomputed before use.

---

## 2. Stable research findings before the macro campaign

### 2.1 Small virtual-edge and hole searches were negative

Multiple finite searches for forced same-color/different-color pairs and neighborhood “hole” gadgets found no useful small forcing object. The adaptive neighborhood campaign reached an exact extinction threshold at 408 selected points, but the resulting mechanism behaved as a covering network rather than a compact local gadget.

The main interpretation is negative but useful: local low-width forcing is unusually weak in the explored families.

### 2.2 G510 and the three phi ports

The G510 configuration contains three exact golden-ratio pairs:

- P1: `(211,489)`
- P2: `(217,490)`
- P3: `(223,488)`

Bare G510 is extremely flexible at these ports. All 8 same/different combinations of the three pairs were 5-SAT, and all 202 set partitions of the six endpoints using at most five colors were realized.

This eliminates any claim that the bare G510 geometry itself forces a useful phi-port relation.

### 2.3 The P2 conditional lemma

A set `C88` of 88 same-color pair conditions was found such that

\[
G510\land C88
\]

is 5-colorable, while

\[
G510\land C88\land(c(217)\ne c(490))
\]

is 5-UNSAT.

The equality-condition graph is a forest and does not trivially connect the port endpoints. The conditions are deletion-minimal in the tested orders. The mechanism is global: multiple edge-core extractions produced closely matching cores and a large common backbone.

The strongest safe statement is:

> Under `C88`, P2 is forced monochromatic in every 5-coloring.

It is not an unconditional unit-distance forcing lemma because `C88` is external.

### 2.4 Three-point strengthening

Semantic-interface analysis found that `C88` forces the three vertices

\[
217,489,490
\]

to have one color. Their pairwise distances are

\[
\sqrt5,\quad 2,\quad \varphi.
\]

The support-3 interface was the transitive chain through vertex 489. Exhaustive non-chain support-3 search was negative.

### 2.5 ROT_T4 amplification

Rotating a copy about vertex 489 by

\[
\omega_4=\frac{7+i\sqrt{15}}8
\]

makes the two images of vertex 490 a unit-distance pair. Two conditional copies therefore produce a contradiction when both copies satisfy their `C88` conditions.

The resulting 1019-vertex conditional machine is 5-UNSAT under all 118 condition blocks. Mixed block MUS deletion found all 118 blocks indispensable in the fixed language. Pairwise transfer between the 59 left and 59 right blocks was absent.

Safe interpretation:

> ROT_T4 is an effective final contradiction amplifier for the given conditions, but did not generate or replace those conditions.

### 2.6 Distributed semantic-interface campaign

A/B were defined by

\[
A=H^*\land C88,
\qquad
B=H^*\land(c(217)\ne c(490)).
\]

Searches over low-width equality observations showed:

- support 2: no interface;
- support 3: only the transitive-chain degeneration;
- port-containing support 4: completely excluded by certificate search;
- extensive port-excluding and distributed searches: many finite-library classifiers, all refilled by exact A/B countermodel pairs.

The available session checkpoint contains 15,401 A/B deceit pairs in `semantic/distforge_pairs.npz`. Earlier JSON traces contain subsets and the evolution history.

The conclusion is not “no distributed interface exists.” It is:

> Small finite classifiers repeatedly overfit the current deceit-pair library; exact two-copy oracles generate new matching-state pairs.

---

## 3. Macro-particle campaign

### 3.1 Origin

A small conditional particle based on a Moser-spindle structure was used as a geometric copy template. Many isometric copies were attached by matching two-point configurations. The purpose was to replace explicit color conditions with a large unit-distance closure whose copies collectively constrain 5-colorings.

The exact reconstruction of the session-only 13-observation/19-edge derivation is not frozen, but the resulting 16-vertex macro template is embedded as the first 16 vertices of the current macro graphs and used by the supplied scanners.

### 3.2 First one-step closures

A phi-pair recursive closure stopped without generating new useful phi pairs. An all-unit-edge-sharing closure was still 5-colorable. An all-two-point-sharing closure produced a 6621-vertex candidate that initially looked hard but was later given a verified 5-coloring.

This established the macro CEGIS loop:

1. find a verified 5-coloring;
2. find template copies not extendable under that coloring;
3. add selected copies;
4. reduce to a 5-core;
5. search for another 5-coloring;
6. extend and independently verify it.

### 3.3 Core-robust correction

An implementation-level conceptual issue was found: a copy that kills a full coloring may cease to kill it after low-degree vertices are recolored during core extension. The scanner was strengthened to use only fixed 5-core vertices when judging incompatibility. These are called **core-robust killers**.

A separate restoration bug was also fixed: domination deletions and low-degree deletions must be restored in their original interleaved reverse order. The current `reduce_graph.py` stores `reduction_ops`, and `extend_core_solution.py` replays those operations correctly.

### 3.4 Progress through step 27

The graph grew to:

\[
|V|=66,033,\qquad |E|=3,046,415.
\]

It remained 5-colorable. The verified coloring and checkpoint are available in the earlier step 27 archive, but step 30 supersedes it.

### 3.5 Multi-model CEGIS: steps 27–30

To reduce overfitting to one coloring, several color-permutation-distinct 5-colorings were generated at each step. Candidate copies were evaluated against all retained models, and copies killing every model were selected with support diversity.

#### Step 27 to 28

- models: 20
- candidates: 5000
- kill-all candidates: 792
- selected: 100
- result: 5-SAT

#### Step 28 to 29

- models: 11
- candidates: 5000
- kill-all candidates: 2077
- selected: 100
- result: 5-SAT

#### Step 29 to 30

- models: 9
- candidates: 5000
- kill-all candidates: 3227
- selected: 100
- result: 5-SAT

The increasing kill-all fraction cannot be interpreted monotonically because the model-pool sizes and diversity differ.

---

## 4. Current checkpoint: step 30

### Graph

\[
|V|=68,802,
\qquad
|E|=3,216,000.
\]

### Reduced core

\[
|V_{core}|=14,886,
\qquad
|E_{core}|=108,924.
\]

### Verified 5-coloring

Color class sizes:

\[
(12,868,16,090,14,228,12,774,12,842).
\]

Every registered edge was checked and has differently colored endpoints.

### Hashes

```text
graph SHA-256
32ba5afa55e88eee5d21821a64526b0704a46496915d8ed8c7f7639c86b0ce98

colors SHA-256
1abc6088fd5c152b3a2497d24e2c1803a4894fdc266dcd7f7fec50a4ff86ca4e
```

### Floating geometry check

Maximum registered-edge error:

\[
2.9993509054\times10^{-7}.
\]

No registered edge exceeded the exploratory tolerance \(3\times10^{-7}\).

### Mathematical status

Step 30 is not a lower-bound witness. It has a verified 5-coloring.

---

## 5. Exact continuation point

The next experiment is step 30 to step 31, with a broader model pool.

### Default registered experiment

1. Verify step 30 hashes and coloring.
2. Generate 50 global-color-permutation-distinct 5-colorings of step 30.
3. Generate candidates from at least 10 randomized geometric scan orders, 500 candidates each.
4. Evaluate every candidate against every retained model.
5. Select 100 candidates that kill all retained models and cover diverse fixed-core supports.
6. Add them atomically to form step 31.
7. Reduce step 31 using low-degree and domination reductions.
8. Seed the new core with the step 30 coloring.
9. Run a large TabuCol portfolio.
10. If a 5-coloring is found, extend it and verify every edge.
11. If no 5-coloring is found within budget, report `UNKNOWN` and escalate to an exact SAT solver. Do not report UNSAT.

The supplied `scripts/resume_step31.sh` implements this pipeline with stage checkpoints.

---

## 6. Priority improvements for local work

### 6.1 Generate a genuinely diverse model pool

Do not retain models merely because their raw color vectors differ. Canonicalize global color permutations and measure Hamming distance after optimal color alignment. Prefer farthest-point sampling over the model set.

A practical target is 50–100 models with broad pairwise distance on the 5-core.

### 6.2 Improve killer selection

“Kill all models” is only the first filter. Optimize candidates by:

1. number of newly covered core support vertices;
2. low support overlap with already selected copies;
3. small number of new geometric vertices;
4. diversity of isometry/orientation orbit;
5. robustness across near-neighbor colorings, not only stored models.

### 6.3 Stop rewriting giant JSON files

The current graph is over 50 MB as JSON and grows rapidly. For long continuation work, introduce:

- immutable base graph;
- append-only placement deltas;
- binary coordinate arrays;
- sorted binary edge arrays;
- a materialization step only for checkpoints.

This is the main engineering improvement for steps beyond 31.

### 6.4 Exact-solver escalation

TabuCol is a SAT witness generator, not an UNSAT prover. For a hard candidate:

- encode only the reduced 5-core;
- fix a small color-symmetry-breaking subgraph;
- use CaDiCaL, Kissat or CryptoMiniSat;
- request DRAT/LRAT proof output;
- verify the proof independently.

### 6.5 Exact geometry only after a genuine 5-UNSAT result

The macro search uses approximate coordinate matching. Do not spend the main search budget on exact reconstruction before a convincing exact 5-UNSAT graph exists. Once one exists, reconstruct every placement as an exact isometry over the original algebraic field and independently regenerate the edge set.

---

## 7. Failure modes already encountered

1. **Encoding bug in an AMO condition** produced a false transition. Quantifier-aware checks fixed it.
2. **Raw UNSAT core interpreted as minimal** — later deletion checks showed when a result was actually minimal.
3. **Index-space confusion** between original graph IDs and filtered support-array positions.
4. **Low-degree recoloring escape** made full-coloring killers non-robust.
5. **Restoration ordering bug** left domination-deleted vertices uncolored; fixed by interleaved `reduction_ops` replay.
6. **Finite-library overfitting** occurred in phi-forge, semantic interpolation and macro CEGIS.
7. **Solver timeout interpreted too strongly** — all timeout results must remain `UNKNOWN`.
8. **Large JSON write interrupted** — use temporary files and atomic rename.

---

## 8. Success criteria

A genuine successful endpoint requires all of the following.

### Combinatorial certificate

A finite graph and a complete 5-UNSAT certificate independently checked.

### Geometric certificate

Exact coordinates and exact proof that every graph edge has Euclidean length one.

### Reproducibility

- deterministic graph generator;
- fixed input hashes;
- solver version and command;
- proof checker version and command;
- independent coloring/geometry checker;
- frozen archive and commit/tag.

Until then, the correct status remains exploratory.
