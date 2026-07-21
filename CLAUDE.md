# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`argocli` is a Python CLI for interacting with Argo Workflows over its REST API. It follows a `argocli <command> <action> [options]` pattern (e.g. `argocli workflow list`). Commands and actions are discovered dynamically from the directory structure — there is no central command registry.

## Commands

Dependencies are managed with [uv](https://github.com/astral-sh/uv).

```bash
uv sync                                      # install deps (incl. dev)
source .venv/bin/activate                    # activate venv
uv run pytest                                # run all tests
uv run pytest --cov=argocli --cov-report=term  # tests with coverage
uv run argocli workflow list                 # run the CLI locally
```

Running a single test:

```bash
pytest tests/unit/commands/workflow/test_list.py                              # one file
pytest tests/unit/commands/workflow/test_list.py::TestWorkflowList            # one class
pytest tests/unit/commands/workflow/test_list.py::TestWorkflowList::test_execute_filtered_list  # one method
```

There is no configured linter/formatter in CI (Ruff steps are commented out). `.pylintrc` lives under `tests/`; pylint disables are applied per-file via inline comments.

## Architecture

The CLI is built on the shared **`cac-core`** framework (`>=2.0.1,<3.0.0`), which owns discovery, argument parsing, shell completion, dispatch, and exit-code handling. `argocli` supplies only the package, the command classes, and the lazily-initialized singletons. This mirrors the sibling `cac-jira` project.

**Entry point** (`argocli/__init__.py`): `main = make_main("argocli", "argocli", "Argo CLI tool")` (from `cac_core.cli`). At runtime `make_main`'s runner scans `argocli/commands/` for subdirectories with an `__init__.py` (each is a *command*, e.g. `workflow`) and each public `.py` file inside (each is an *action*, e.g. `list`, `view`; modules starting with `_` are skipped). For action file `foo.py` under command `bar`, it imports the class `BarFoo` (capitalize command + capitalize action). **To add a command or action, just add the file/class following this naming convention — no registration needed.** `argocli/__main__.py` lets `python -m argocli` invoke the same entry point (used by the VS Code debug configs).

**Command execution contract:** actions implement `execute(args)` as straight-line logic that returns an `int` exit code (or `None` = 0) and **may raise freely**. The framework's `Command.run()` wraps `execute()` and routes exceptions through `handle_exception()`. Do not add defensive try/except around client calls in `execute()`.

**Command class hierarchy:**
- `cac_core.command.Command` — external base; provides `--output [json|table]` and `--verbose` via `define_common_arguments`, and the `run()`/`handle_exception()` template.
- `argocli/commands/command.py::ArgoCommand` — eager `self.config` (network-free), a lazy `argo_client` property (resolves `argocli.ARGO_CLIENT` on first access; has a setter for test injection), and an `ArgoCommand.handle_exception` that turns Argo API errors into friendly messages (404 → "Workflow not found.", other `requests` errors → concise message).
- `argocli/commands/workflow/__init__.py::ArgoWorkflowCommand` — adds a required `-n/--name` argument (unless a subclass already defined one, e.g. `list` makes it optional for filtering).
- Concrete actions (`list.py`, `view.py`, `status.py`, `browse.py`) subclass `ArgoWorkflowCommand`.

**Lazy initialization** (`argocli/__init__.py`): `CONFIG` and `ARGO_CLIENT` are exposed via module `__getattr__` and built on first access, not at import time. `_initialize_config()` is network-free (loads `cac_core.config.Config` and runs first-run `ensure_keys` prompts for `server`/`namespace`/`username`); `_initialize_client()` additionally resolves the API token from the system credential store (Keychain on macOS) and constructs the client, `sys.exit(1)`-ing if no token is found. **So importing `argocli` is cheap and side-effect-free** — accessing `CONFIG` only reads local config; accessing `ARGO_CLIENT` requires credentials.

**API client** (`argocli/core/client.py::ArgoClient`): Thin `requests` wrapper around Argo's `/api/v1/workflows/{namespace}` endpoints, using bearer-token auth. **Raise contract** — methods call `response.raise_for_status()` and return the parsed body on success; they never return `None`/`[]` to signal failure (`requests.HTTPError`/`RequestException` propagate to the command's `handle_exception`). `ArgoClientError` is available for non-HTTP failures.

**Output** is handled by `cac_core.output.Output` / `cac_core.model.Model`: commands build a list of `Model` dicts and call `printer.print_models(...)`, which renders as a table or JSON depending on `--output`.

## Configuration

Runtime config lives at `~/.config/argocli/config.yaml` (`server`, `namespace`, `username`). The `argocli/config/argocli.yaml` file is the packaged default template (all values `INVALID_DEFAULT`; on first run, `ensure_keys` prompts for any key still at the sentinel). Any config key can be overridden by an env var `ARGOCLI_<UPPERCASE_KEY>` (e.g. `ARGOCLI_SERVER`).

## Testing conventions

Tests mirror the source tree under `tests/unit/`. `tests/conftest.py` sets `ARGOCLI_*` env vars and patches `keyring.get_password` + the update checker **at module level**, so lazy init is safe the first time a command is instantiated. Command tests instantiate the action class, replace `self.command.argo_client` with a `MagicMock` (hits the property setter), and patch `cac_core.output.Output` to assert on the models passed to `print_models`. Error-path tests make the mock client raise `requests.HTTPError` and assert `command.run(args)` returns a non-zero exit code. Argo API responses are hand-built dicts matching the real workflow JSON shape.
