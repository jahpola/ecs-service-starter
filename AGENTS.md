# AGENTS.md

## Project overview

This repository contains a Python CLI for starting and stopping one or all
services in an Amazon ECS cluster. The implementation is intentionally small:
the CLI and ECS operations live in `main.py`, and unit tests live under
`tests/`.

## Repository layout

- `main.py`: argument parsing, logging, AWS ECS client creation, and service
  operations.
- `tests/conftest.py`: shared pytest fixtures built with `MagicMock`.
- `tests/test_main.py`: unit tests for ECS service operations and pagination.
- `pyproject.toml`: Python version, dependencies, and tool configuration.
- `uv.lock`: locked dependencies; keep it in sync with `pyproject.toml`.
- `.github/workflows/ci.yml`: the authoritative CI checks.
- `sonar-project.properties`: SonarCloud source, test, and coverage settings.

## Environment and setup

- Use Python 3.13 or newer. The repository currently pins Python 3.13 in
  `.python-version`.
- Use `uv` for dependency management and command execution.
- Install all development dependencies with:

  ```bash
  uv sync --all-groups
  ```

- Do not commit virtual environments, caches, coverage output, credentials, or
  local IDE state.
- Let boto3 discover AWS credentials through its standard credential chain.
  Never add credentials, account IDs, or secrets to the repository.

## Development conventions

- Keep changes focused and preserve the CLI's existing behavior unless the task
  explicitly calls for a behavior change.
- Follow the existing straightforward, function-based design. Avoid adding
  abstractions unless they remove real duplication or support a concrete need.
- Use descriptive snake_case names and standard Python conventions.
- Keep lines within the Ruff-configured 120-character limit.
- Use `logging` rather than `print` for runtime status and diagnostics.
- Surface AWS failures clearly. Do not silently catch `ClientError` or report a
  failed ECS operation as successful.
- Preserve the mutually exclusive CLI choices:
  - exactly one of `--service` and `--all`
  - exactly one of `--start` and `--stop`
- Preserve the default start count of one unless requirements explicitly
  change it.
- Continue to paginate `list_services`; do not assume all services fit on one
  response page.

## Testing

- Add or update pytest tests for every behavior change.
- Keep unit tests deterministic and offline. Mock boto3 clients and paginators;
  tests must not require AWS credentials or make network calls.
- Reuse fixtures in `tests/conftest.py` when practical.
- Cover success paths, empty results, pagination, defaults, and relevant error
  paths.
- Run the focused test suite with coverage:

  ```bash
  uv run python -m pytest tests/test_main.py -v --cov=main --cov-report=xml
  ```

- During iteration, a narrower pytest node selector is acceptable, but run the
  full focused suite above before finishing.

## Linting, formatting, and type checking

Run these checks before considering a code change complete:

```bash
uv run ruff check main.py tests/test_main.py
uv run ruff format --check main.py tests/test_main.py
uv run ty check .
uv run python -m pytest tests/test_main.py -v --cov=main --cov-report=xml
```

If formatting is required, apply it with:

```bash
uv run ruff format main.py tests/test_main.py
```

CI currently runs Ruff checks, Ruff formatting verification, pytest, coverage,
and SonarCloud analysis. Keep local validation aligned with
`.github/workflows/ci.yml`.

## Dependency changes

- Add or remove dependencies through `uv`; do not edit `uv.lock` manually.
- Commit both `pyproject.toml` and the regenerated `uv.lock` when dependencies
  change.
- Avoid introducing runtime dependencies when the standard library or an
  existing dependency is sufficient.

## Documentation

- Update `README.md` when setup steps, command-line flags, prerequisites, or
  user-visible behavior change.
- Keep examples executable and consistent with the current CLI syntax.
