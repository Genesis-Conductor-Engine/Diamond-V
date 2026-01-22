# Repository Guidelines

## Project Structure & Module Organization
- `genesis-q-mem/` is the primary codebase for Q-Mem benchmarking and the Yennefer subsystem (daemons, APIs, and dashboards).
- `contracts/` contains Solidity smart contracts managed by Hardhat (see `hardhat.config.js`).
- `deploy/`, `scripts/`, and top-level shell scripts (`start_*.sh`, `verify_*.sh`) host orchestration and automation.
- GPU cache tooling and benchmarks live at the root (e.g., `gpu_cache_*.py`, `benchmark_*.py`).
- Additional subprojects (e.g., `q-mem-stack/`, `genesis_workspace/`) are standalone and should be treated as separate modules.

## Build, Test, and Development Commands
- `cd genesis-q-mem && pip install -r requirements.txt` installs Python dependencies.
- `cd genesis-q-mem && make` builds the Ground Truth C library (`libgroundtruth.so`).
- `cd genesis-q-mem && make test` runs the C/Python verification tests.
- `cd genesis-q-mem && ./start_live_bench_v2.sh` starts the live benchmark + API gateway; use `--mini` for a short validation run.
- `cd genesis-q-mem && ./start_yennefer_full_system.sh` launches the full Yennefer service set.
- `npm test` runs Hardhat tests for `contracts/` (add tests under `test/` when present).

## Coding Style & Naming Conventions
- Python: use `black` (line length 120), `flake8`, and `mypy` as referenced in `genesis-q-mem/CLAUDE.md`.
- Follow existing naming patterns: `snake_case.py` for modules, `start_*.sh` for launchers, and `PascalCase.sol` for contracts.
- Keep configuration in `.env` and shared memory paths under `/dev/shm/` consistent with existing services.

## Testing Guidelines
- Primary validation is script-driven (e.g., `quick_perf_test.py`, `redline_benchmark.py`, `test_qmcp_api.py`).
- For Solidity, prefer `*.test.js` under `test/` and run via `npm test`.
- Document any performance baselines or mode changes (real vs. simulated) in your PR description.

## Commit & Pull Request Guidelines
- No Git history is present in this directory; default to Conventional Commits (e.g., `feat:`, `fix:`) unless otherwise specified.
- PRs should include: purpose, tests run (with commands), and any impact on running services or ports.
- If changes affect dashboards or APIs, include screenshots or example `curl` output.

## Security & Configuration Tips
- Never commit API keys or credentials; generate or load them at runtime (e.g., via `qmem_auth.py`).
- Be cautious when editing systemd units or scripts that touch `/etc/` and `/dev/shm/`.
