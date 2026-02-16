# IDF — Claude Code Plugin for ESP-IDF Development

Claude Code plugin with commands and tools for ESP-IDF development.

## Plugin Structure

- `.claude-plugin/plugin.json` — Plugin manifest (name, version, metadata)
- `commands/*.md` — Slash command prompts (at plugin root, NOT inside `.claude-plugin/`)

## Available Commands

### Code Review
- `/idf:review-changes` — Review staged and unstaged changes on the current branch
- `/idf:review-staged` — Review only staged changes
- `/idf:review-branch [base] [head]` — Review changes between two branches before creating an MR/PR
- `/idf:review-mr <URL>` — Review a GitHub PR or GitLab MR by URL

## Conventions

- Each command file is a self-contained prompt
- `$ARGUMENTS` is the placeholder for user-supplied input
- Commands should work without any external dependencies beyond `git`, `gh` (GitHub CLI), and `glab` (GitLab CLI)
