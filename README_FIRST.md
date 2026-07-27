# CNP6 handoff — read this first

**Snapshot date:** 2026-07-27 (Asia/Tokyo)  
**Current status:** no proof of \(\chi(\mathbb R^2)\ge 6\). The latest macro graph, step 30, has a fully verified 5-coloring.

## Recommended execution environment

Use **VS Code + WSL2 Ubuntu**. The existing C++ uses GNU-specific headers such as `bits/stdc++.h`; native MSVC in full Visual Studio will not compile it without source changes. ChatGPT Desktop is useful for reviewing logs and preparing patches, but it does not remove execution-time limits. The long computation should run as a local OS process.

Quick start inside a VS Code Remote-WSL terminal:

```bash
cd /mnt/c/path/to/CNP6_HANDOFF_2026-07-27
bash scripts/setup_wsl.sh
bash scripts/verify_current.sh

tmux new -s cnp6
bash scripts/resume_step31.sh 2>&1 | tee logs/step31-console.log
# detach: Ctrl-b, then d
# reattach later: tmux attach -t cnp6
```

VS Code tasks are included. Open `CNP6.code-workspace`, then run:

- `CNP6: Verify step30`
- `CNP6: Resume step31`

The pipeline is resumable. Completed stages are marked under `work/step31/*.done`; rerunning does not repeat them.

## What is in this package

- `docs/HANDOFF_FULL.md` — complete research and computation handoff
- `docs/LOCAL_RUN_WINDOWS.md` — Windows/WSL/VS Code instructions
- `docs/NEXT_EXPERIMENT.md` — exact next experiment and success criteria
- `docs/KNOWN_LIMITS.md` — statements that must not be overclaimed
- `docs/CONTINUATION_PROMPT.md` — prompt to give another coding/research agent
- `current/` — step 30 graph, 5-coloring, 5-core and macro-CEGIS code
- `semantic/` — distributed-interpolant checkpoints and scripts
- `upstream/cnp6_original_snapshot.zip` — original researcher snapshot
- `scripts/resume_step31.sh` — staged local continuation pipeline
- `MANIFEST.sha256` — file integrity list

## Current verified checkpoint

```text
step:       30
vertices:   68,802
edges:      3,216,000
5-coloring: verified on every registered edge
graph SHA-256:
32ba5afa55e88eee5d21821a64526b0704a46496915d8ed8c7f7639c86b0ce98
colors SHA-256:
1abc6088fd5c152b3a2497d24e2c1803a4894fdc266dcd7f7fec50a4ff86ca4e
```

Run `bash scripts/verify_current.sh` before continuing.
