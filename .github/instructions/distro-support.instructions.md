---
description: "Project-specific guidelines for distro-support, a Python library for querying Linux distribution support dates."
applyTo: "**"
---

# distro-support Development Guidelines

`distro-support` is a Python library that provides support date information for Linux
distributions. It ships JSON data files for each supported distro and exposes a simple
`get_support_range()` API, plus optional online downloaders that fetch live data from
upstream sources.

## Project Structure

```
src/distro_support/
    __init__.py                  # Public API: get_support_range()
    _distro.py                   # Core dataclasses: SupportRange, DistroInfo
    errors.py                    # Exceptions: UnknownDistributionError, etc.
    <distro>.py                  # Per-distro module (e.g. debian.py, ubuntu.py)
    <distro>.json                # Bundled support data (e.g. debian.json)
    _debian_like_downloader.py   # Shared downloader for Debian-family distros
    _rhel_downloader.py          # Downloader for RHEL-family distros
tests/
    test_distro.py
    test_get_support_range.py
    test_debian_like_downloader.py
    test_alpine_downloader.py
tools/
    update.py                    # Regenerates all JSON data files from upstream
```

## Tooling

- **Package manager**: `uv` — use `uv run <cmd>` inside the project, never bare `pip`
- **Test runner**: `pytest` — run with `uv run pytest` or `make test`
- **Linter/formatter**: `ruff` — run with `make lint` or `uv run ruff check`
- **Type checker**: `ty` (astral-ty snap) — run with `make lint`
- **Pre-commit**: configured in `.pre-commit-config.yaml`; CI enforces it
- **Build**: `make` wraps common tasks; `make help` lists all targets
- **LXD testing**: `make test-lxd LXD_DISTRO=<distro>/<version>` runs the test suite
  inside an LXD container to verify cross-distro compatibility

## Core Data Model

`SupportRange` (in `_distro.py`) is the central dataclass:

```python
@dataclasses.dataclass(kw_only=True, slots=True)
class SupportRange:
    distribution: str
    version: str
    begin_support: Optional[datetime.date]
    end_support: Optional[datetime.date]
    begin_dev: Optional[datetime.date] = None
    end_extended_support: Optional[datetime.date] = None
```

- All date fields are `Optional[datetime.date]` — a `None` means the date is unknown
- `end_extended_support` represents ESM/LTS extended support (e.g. Ubuntu Pro)
- `from_json(data: dict[str, Optional[str]])` is the standard constructor from JSON

## JSON Data Files

Each distro's bundled data is a JSON object keyed by version string:

```json
{
    "12": {
        "eol": "2026-06-30",
        "release": "2021-08-14"
    },
    "": {
        "release": null,
        "eol": null
    }
}
```

- Keys are version strings; an empty string `""` represents the rolling/sid release
- Date values are ISO 8601 strings (`"YYYY-MM-DD"`) or `null`
- Keep versions in **ascending numeric order**; keep keys within each version object
  in a consistent order (typically `release` before `eol`/`eol-*`)
- The `tools/update.py` script regenerates these files from upstream; run it after
  adding a new distro or refreshing data, then commit the updated JSON

## Adding a New Distribution

1. Create `src/distro_support/<distro>.json` with version data
2. Create `src/distro_support/<distro>.py` that exposes `get_distro_info()` (returning
   a `dict[str, SupportRange]`) — either use a bundled JSON file or a downloader
3. Register the new module so `get_support_range()` finds it
4. Add the distro to the CI matrix in `.github/workflows/pr.yaml` (both `x86-64` and
   `arm64` lists where applicable; Linux Mint is x86-64 only)
5. Add `make test-lxd LXD_DISTRO=<distro>/<version>` verification locally before PR

## Downloaders

Downloaders live in `_<family>_downloader.py` and follow this pattern:

- Accept an optional `requests.Session` (or similar) for testability
- Raise `RuntimeError` for unexpected HTTP status codes (not 200)
- Return `dict[str, SupportRange]`
- Use `(row.get("field") or None)` when reading CSV/API fields that may be empty
  strings — empty string is falsy but not `None`, and `datetime.date.fromisoformat("")`
  raises `ValueError`

## Testing Conventions

- Use `pytest` with `freezegun` for date-sensitive tests
- Mock HTTP calls with `unittest.mock.patch` on `requests.get` (or the session method)
- Test files mirror source files: `test_<module>.py`
- Each downloader should have tests for: normal data, empty optional fields, HTTP errors
- Keep test parametrization flat and readable; avoid deeply nested fixtures

## Type Annotations

- All public functions and methods must be fully annotated
- Use `Optional[X]` (not `X | None`) for consistency with the existing codebase
- Use `typing_extensions` for features not yet in the stdlib minimum (currently 3.10)
- `ty` (astral-ty) is the primary type checker; it is stricter than mypy on narrowing —
  assign to a local variable before an `is None` check rather than checking
  `data.get("key") is None` directly

## CI Matrix

The `test-distros` GitHub Actions job tests against 22 distros across two runners:

- **x86-64** (`ubuntu-latest`): 20 distros including Linux Mint
- **arm64** (`ubuntu-24.04-arm`): 18 distros (Mint excluded)

LXD containers are launched in parallel; the `test-lxd` Make target handles network
readiness (default route + DNS), package installation with retry, and file transfer via
`tar` pipe (excluding `.venv`, `.git`, `__pycache__`).
