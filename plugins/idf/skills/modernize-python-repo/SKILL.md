---
name: modernize-python-repo
description: Guides modernization of Python repositories: pyproject.toml migration, Ruff adoption, config consolidation, CI/CD and Danger workflow updates (GitHub and GitLab). Use when modernizing a Python repo, migrating from setup.py, adopting Ruff, updating Espressif GitHub/GitLab workflows, or migrating from espressif/github-actions/danger_pr_review to shared-github-dangerjs.
invoke: user
---

# Modernize Python Repository

## Quick Start

**Order matters**: Package config first → linting → tool consolidation → CI/CD → cleanup. Test after each major change. Use feature branches. Keep commits atomic.

## 1. GitHub Danger Workflow Migration (Espressif)

Before or alongside other CI changes, migrate PR review workflows:

### Check for legacy Danger usage
- [ ] Search GitHub workflows for `espressif/github-actions/danger_pr_review` or `danger_pr_review`; note which workflow files and jobs use it
- [ ] If the repo uses GitLab, search `.gitlab-ci.yml` and related config for Danger/MR review usage and note which jobs use it

### Migrate to shared-github-dangerjs
- [ ] Replace references to `espressif/github-actions/danger_pr_review` with the shared Danger workflow from **https://github.com/espressif/shared-github-dangerjs**
- [ ] Use the reusable workflow or action from `espressif/shared-github-dangerjs` as documented in that repo
- [ ] Preserve any repo-specific Danger config (e.g. `dangerfile.js`, `.dangerjs.yml`) and ensure the new workflow uses it
- [ ] Remove deprecated `danger_pr_review` job/step definitions
- [ ] Verify the new workflow runs on the same triggers (e.g. pull_request) and has required permissions

**What to change**: In `.github/workflows/*.yml`, replace the action or workflow reference from the old `danger_pr_review` source to `espressif/shared-github-dangerjs` (call pattern depends on how the shared repo exposes the workflow—check its README).

### GitLab: MR review / Danger
- [ ] If the repo uses GitLab and has MR review or Danger: locate config (e.g. `.gitlab-ci.yml` jobs, `dangerfile.js`, `.dangerjs.yml`)
- [ ] Align with the same Danger/source approach as GitHub (e.g. `espressif/shared-github-dangerjs` or equivalent); update includes and job definitions in `.gitlab-ci.yml` to match the pattern used in `.github/workflows`
- [ ] Preserve repo-specific Danger config and triggers (merge_request, etc.)

## 2. Package Configuration

### Check current setup
- [ ] Check if project uses `setup.py` or `setup.cfg`
- [ ] Identify all metadata (name, version, dependencies, entry points) and any dynamic versioning

### Migrate to pyproject.toml
- [ ] Create `pyproject.toml` with `[build-system]` (setuptools or other backend) and `[project]`
- [ ] Move all metadata to `[project]`; set up dynamic version if needed (`[tool.setuptools.dynamic]`)
- [ ] Migrate runtime deps to `dependencies`, dev deps to `[project.optional-dependencies.dev]`
- [ ] Preserve all entry points (console_scripts, plugins, etc.)
- [ ] **Keep the project's minimal Python requirement**: preserve existing `requires-python` and Python version classifiers; do not drop support for older Python versions in this modernization. Raising or dropping supported Python versions is a breaking change and should be done in a separate, explicit change.
- [ ] Update Development Status classifier only as needed
- [ ] Remove `setup.py` and `setup.cfg` after validation. Build: `python -m build`; install and test.

## 3. Linting: Migrate to Ruff

### Check current tools
- [ ] Identify current linters (flake8, pylint), formatters (black, autopep8), and isort; review `.flake8`, `setup.cfg`, or other config

### Migrate to Ruff
- [ ] Add `[tool.ruff]` in `pyproject.toml` (line-length, target-version). Set `target-version` to match the project's minimal supported Python (do not raise it as part of this modernization).
- [ ] Enable rule sets: **F** (Pyflakes), **E/W** (pycodestyle), **I** (isort), **UP** (pyupgrade)
- [ ] Map existing ignore rules from flake8/pycodestyle
- [ ] Run `ruff check . --fix`. Update pre-commit to `astral-sh/ruff-pre-commit`
- [ ] Remove `.flake8` and old isort/flake8 configs and hooks

## 4. Tool Config Consolidation

### Check existing configs
- [ ] Identify separate config files (`.coveragerc`, `pytest.ini`, `.mypy.ini`, etc.) and tool sections in `setup.cfg`

### Consolidate into pyproject.toml
- [ ] Move pytest to `[tool.pytest.ini_options]`, mypy to `[tool.mypy]`, coverage to `[tool.coverage.*]`
- [ ] Keep only tools that don't support pyproject.toml in separate files
- [ ] Remove old config files after migration

## 5. Commitizen / Changelog

### Check current setup
- [ ] Check if commitizen or similar is used; review commit conventions

### Espressif: czespressif
- [ ] Replace `commitizen` with `czespressif` in dev dependencies
- [ ] Add `[tool.commitizen]` with `name = "czespressif"`, configure `bump_message` to Espressif convention
- [ ] Remove custom `change_type_order` and `change_type_map` (use plugin defaults). Test: `cz example`

### Others: standard Commitizen
- [ ] Add/update `[tool.commitizen]` with appropriate `name` (e.g. `cz_conventional_commits`); configure version files, tag format, changelog settings

## 6. CI/CD (excluding Danger)

### PyPI publishing
- [ ] If publishing to PyPI: set up trusted publishing (OIDC); use `pypa/gh-action-pypi-publish@release/v1`, `id-token: write`, environment (e.g. `pypi`), `skip-existing: true`
- [ ] Remove manual version checks and `PYPI_PROJECT_TOKEN` dependency

### GitHub Actions
- [ ] Review and consolidate duplicate workflows; update action versions; use org reusable workflows where available

### GitLab CI
- [ ] Apply the same modernization as GitHub where applicable: in `.gitlab-ci.yml`, update jobs for lint (Ruff), format, test matrix (keep minimal Python version), coverage, and optional PyPI publish
- [ ] Use the same Ruff/pre-commit and test commands as in GitHub workflows; align job names and stages with the consolidated GitHub layout
- [ ] Remove or replace deprecated GitLab jobs that duplicated old flake8/isort/setup.py-based steps

### Espressif Jira sync
- [ ] Consolidate to one workflow; use `espressif/sync-jira-actions@v1` with multi-trigger (issues, comments, schedule, workflow_dispatch) and permissions (contents: read, issues: write, pull-requests: write)

## 7. Testing and Validation

### Pre-migration
- [ ] Run existing tests for baseline; document unrelated failures and current lint/format issues

### Post-migration
- [ ] Build: `python -m build`; install: `pip install dist/*.whl`; verify entry points
- [ ] Run test suite; run `ruff check .` and `ruff check . --select I`; run `mypy .` if configured
- [ ] Optional: security scans (CodeQL, bandit, safety)

### Review
- [ ] Review all modified files; ensure no unintended changes and backwards compatibility where needed

## 8. Documentation and Cleanup

### Docs
- [ ] Update CONTRIBUTING.md (linting commands, pre-commit); README installation if needed; version/commitizen docs

### Remove deprecated files
- [ ] `setup.py`, `setup.cfg` (if migrated); `.flake8` (if using Ruff); consolidated config files; old GitHub workflow files and obsolete GitLab CI job definitions

### .gitignore
- [ ] Ignore `dist/`, `build/`, `*.egg-info/`, `.ruff_cache/`

## 9. Pre-commit Hooks

- [ ] Review `.pre-commit-config.yaml`; update Ruff to latest, remove hooks replaced by Ruff, update others
- [ ] Test: `pre-commit run --all-files`

## Notes

- **Python support**: Keep the project's minimal Python requirement; do not drop older Python versions in this modernization. That is a breaking change and should be done separately.
- Test frequently after each major change; use feature branches; document decisions; consider downstream impact.

## Optional Enhancements

- Add `ruff format` (replaces black); enable more Ruff rules (B, C4, SIM); strict mypy; dependabot; pre-commit.ci; coverage reporting.
