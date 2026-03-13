# IDF — Claude Code Plugin for ESP-IDF Development

Claude Code plugin with skills for ESP-IDF development.

## Plugin Structure

- `.claude-plugin/plugin.json` — Plugin manifest (name, version, metadata)
- `skills/*/SKILL.md` — Skill definitions (at plugin root, NOT inside `.claude-plugin/`)

## Available Skills

### Code Review
- `/idf:review [URL]` — Review local changes (no args) or a GitHub PR / GitLab MR (pass URL). Offers to post draft review comments for MRs/PRs.

### Python Modernization
- `/idf:modernize-python-repo` — Run the full Python repository modernization checklist

### Status Report
- `/idf:status-report` — Generate a weekly status report from GitHub and GitLab activity

## Conventions

- Each skill directory contains a `SKILL.md` with a self-contained prompt
- `$ARGUMENTS` is the placeholder for user-supplied input
- Skills should work without any external dependencies beyond `git`, `gh` (GitHub CLI), `glab` (GitLab CLI), and `python3`
