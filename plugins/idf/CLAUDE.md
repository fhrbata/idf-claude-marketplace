# IDF — Claude Code Plugin for ESP-IDF Development

Claude Code plugin with skills for ESP-IDF development.

## Plugin Structure

- `.claude-plugin/plugin.json` — Plugin manifest (name, version, metadata)
- `skills/*/SKILL.md` — Skill definitions (at plugin root, NOT inside `.claude-plugin/`)

## Available Skills

### Code Review
- `/idf:review-changes` — Review staged and unstaged changes on the current branch
- `/idf:review-staged` — Review only staged changes
- `/idf:review-branch [base] [head]` — Review changes between two branches before creating an MR/PR
- `/idf:review-mr <URL>` — Review a GitHub PR or GitLab MR by URL

### Python Modernization
- `/idf:modernize-python-repo` — Run the full Python repository modernization checklist

### Status Report
- `/idf:status-report` — Generate a weekly status report from GitHub and GitLab activity

## Code Review Guide

All review skills follow this shared methodology and criteria. Individual skills define their own mechanics (how to fetch diffs, output format, etc.) but defer here for the analytical approach.

### Review Methodology

1. **Understand the purpose first** — Read description/commits before code. Understand what the author claims to have done and why.
2. **Read all changed files in full** — Not just the diff. Understand surrounding context, function signatures, naming conventions, existing patterns.
3. **Verify description claims against code** — If description says "migrated X to Y", check every instance. If it claims "config Z is defined in component W", verify. Discrepancies between stated intent and actual code are high-value findings.
4. **Check cross-file consistency** — When the same pattern appears in multiple changed files, systematically compare: naming, parameters, error handling, comments. Inconsistencies are common and impactful.
5. **Compare parallel implementations** — If the change modifies multiple implementations of the same concept (e.g., v1 and v2, different backends), compare for behavioral parity. Document differences and verify they are intentional.
6. **Trace edge cases** — For new/modified functions, consider all parameter values: empty lists, duplicate calls, invalid types, boundary values. What happens when `type` is INTERFACE vs PRIVATE vs PUBLIC?
7. **Check documentation accuracy** — Verify comments/docstrings match actual behavior. Check for imprecise wording, stale comments, claims that are technically incorrect.

### Review Criteria

- **Correctness** — Logic errors, edge cases, off-by-one, null handling, race conditions.
- **Consistency** — Naming, behavior, API symmetry across files and implementations. Same concept should use same names. Parallel implementations should have equivalent behavior or documented differences.
- **Migration correctness** — When replacing a lenient operation with a stricter one, verify existing arguments are actually valid. Don't assume correctness because the old code "worked."
- **Error handling** — Missing error paths, swallowed errors, resource leaks, unclear error messages.
- **Documentation accuracy** — Comments match behavior, precise wording, no stale comments.
- **Security** — Hardcoded secrets, insecure defaults, improper input validation.
- **Performance** — Unnecessary allocations, algorithmic complexity, blocking calls.
- **Best practices** — Framework/language idioms, deprecated APIs, missing tests for new logic.

## Conventions

- Each skill directory contains a `SKILL.md` with a self-contained prompt
- `$ARGUMENTS` is the placeholder for user-supplied input
- Skills should work without any external dependencies beyond `git`, `gh` (GitHub CLI), `glab` (GitLab CLI), and `python3`
