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
│       │   ├── review/
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

#### `/idf:review`

Reviews code changes. Without arguments, reviews all local changes on the current branch — working tree, staged, and unpushed commits vs upstream. With a GitHub PR or GitLab MR URL, fetches and reviews that MR/PR, then offers to post findings as draft review comments.

```
/idf:review                                                    # review local changes
/idf:review https://github.com/org/repo/pull/123               # review a GitHub PR
/idf:review https://gitlab.com/org/repo/-/merge_requests/42    # review a GitLab MR
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
