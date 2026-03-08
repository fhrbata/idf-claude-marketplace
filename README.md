# IDF — Claude Code Marketplace for ESP-IDF Development

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin marketplace with skills for ESP-IDF development.

## Installation

1. Add the marketplace — in Claude Code, run:

   ```
   /plugin marketplace add fhrbata/idf-claude-marketplace
   ```

2. Install the plugin from the marketplace:

   ```
   /plugin install idf@fhrbata-idf-claude-marketplace
   ```

### Local development / testing

For plugin development, you can clone the repository and add it as a local marketplace:

```bash
git clone https://github.com/fhrbata/idf-claude-marketplace
```

Then in Claude Code:

```
/plugin marketplace add ./path/to/idf-claude-marketplace
```

## Marketplace Structure

```
idf-claude-marketplace/
├── .claude-plugin/
│   └── marketplace.json                    ← Marketplace catalog
├── plugins/
│   └── idf/
│       ├── .claude-plugin/
│       │   └── plugin.json                 ← Plugin manifest
│       ├── skills/
│       │   ├── review-changes/
│       │   │   └── SKILL.md
│       │   ├── review-staged/
│       │   │   └── SKILL.md
│       │   ├── review-branch/
│       │   │   └── SKILL.md
│       │   ├── review-mr/
│       │   │   └── SKILL.md
│       │   ├── modernize-python-repo/
│       │   │   └── SKILL.md
│       │   └── status-report/
│       │       ├── SKILL.md
│       │       └── scripts/
│       │           └── report.py           ← Data collection script
│       └── CLAUDE.md
├── README.md
└── .gitignore
```

## Skills

### Code Review

#### `/idf:review-changes`

Reviews all staged and unstaged changes on the current branch. Provides a comprehensive code review covering correctness, security, performance, code style, and more.

```
/idf:review-changes
```

#### `/idf:review-staged`

Reviews only staged changes (what would be committed). Same review criteria as `review-changes`.

```
/idf:review-staged
```

#### `/idf:review-branch`

Reviews changes between two branches before creating a merge request or pull request. Useful for a pre-submission review to catch issues early.

```
/idf:review-branch                       # current branch vs default branch
/idf:review-branch feature-xyz           # feature-xyz vs default branch
/idf:review-branch main feature-xyz      # feature-xyz vs main
```

#### `/idf:review-mr`

Reviews a merge request (GitLab) or pull request (GitHub) by URL. Fetches the diff and provides a full review.

```
/idf:review-mr https://gitlab.com/org/repo/-/merge_requests/42
/idf:review-mr https://github.com/org/repo/pull/123
```

### Python Modernization

#### `/idf:modernize-python-repo`

Guides modernization of Python repositories: pyproject.toml migration, Ruff adoption, config consolidation, CI/CD and Danger workflow updates (GitHub and GitLab).

```
/idf:modernize-python-repo
```

### Status Report

#### `/idf:status-report`

Collects activity data from GitHub and GitLab APIs, then generates a formatted weekly status report.

```
/idf:status-report
/idf:status-report --days 14
```

Requires configuration — see the [skill SKILL.md](plugins/idf/skills/status-report/SKILL.md) for setup instructions.

## Requirements

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
- `git`
- `gh` (GitHub CLI) — for reviewing GitHub pull requests
- `glab` (GitLab CLI) — for reviewing GitLab merge requests
- `python3` + `requests` — for the status-report skill

## License

MIT
