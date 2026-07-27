# Local execution on Windows

## Recommended: VS Code + WSL2

This is the least fragile setup.

### 1. Install

In an administrator PowerShell:

```powershell
wsl --install -d Ubuntu
```

Install VS Code and the **WSL** extension. Reboot if Windows requests it.

### 2. Extract the package

Use a short ASCII-only path, for example:

```text
C:\cnp6\CNP6_HANDOFF_2026-07-27
```

Very long Windows paths and cloud-synchronized folders should be avoided. The graph JSON files are large and are rewritten during graph construction.

### 3. Open in WSL

From PowerShell:

```powershell
cd C:\cnp6\CNP6_HANDOFF_2026-07-27
wsl
code .
```

The lower-left corner of VS Code should say `WSL: Ubuntu`.

### 4. Install build tools

Inside the WSL terminal:

```bash
bash scripts/setup_wsl.sh
```

### 5. Verify the checkpoint

```bash
bash scripts/verify_current.sh
```

### 6. Run without UI timeouts

```bash
tmux new -s cnp6
bash scripts/resume_step31.sh 2>&1 | tee logs/step31-console.log
```

Detach without stopping the computation:

```text
Ctrl-b, then d
```

Reconnect:

```bash
tmux attach -t cnp6
```

The process survives closing VS Code. It does not survive a Windows shutdown unless separately configured to restart.

## Why not ChatGPT Desktop as the executor?

The desktop app does not turn tool calls into unrestricted local background jobs. Use it to inspect logs, review code and decide the next experiment. Run the actual computation in WSL, PowerShell, a terminal multiplexer, or a scheduled local process.

## Full Visual Studio

The current C++ sources use GNU facilities, notably:

```cpp
#include <bits/stdc++.h>
```

Therefore the native MSVC compiler is not the direct path. Full Visual Studio can still be used with a Linux/WSL target, but VS Code Remote-WSL is simpler.

## Native Windows alternative: MSYS2

Install MSYS2 and open the UCRT64 shell:

```bash
pacman -Syu
pacman -S --needed mingw-w64-ucrt-x86_64-gcc python git make zip
```

Then run the shell scripts from that environment. WSL remains preferable because `tmux`, GNU `timeout`, process signals and path handling match the supplied scripts.

## Hardware

Practical baseline:

- 8 CPU cores
- 32 GB RAM
- SSD with at least 30 GB free

Preferred:

- 16 or more CPU cores
- 64 GB RAM
- fast NVMe SSD

The step 30 graph has 3.2 million edges. The main bottleneck is often JSON parsing and rewriting rather than pure SAT/coloring time.

## Preventing lost work

The supplied pipeline follows these rules:

1. Each expensive stage writes to its own directory.
2. Stage completion is recorded by a `.done` file.
3. New graph/core files are written to `.tmp` and renamed only after success.
4. Solver failure means `UNKNOWN`, never `UNSAT`.
5. Logs are appended under `logs/`.

For a multi-day run, back up `work/step31/` and `logs/` periodically.

## Useful environment overrides

```bash
MODELS=80 \
SCAN_SEEDS=20 \
CANDIDATES_PER_SEED=1000 \
SELECT_COUNT=150 \
MODEL_RESTARTS=32 \
MODEL_ITERS=100000000 \
COLOR_RESTARTS=128 \
COLOR_ITERS=500000000 \
bash scripts/resume_step31.sh
```

Start with the defaults. Increasing every parameter at once makes diagnosis difficult.
