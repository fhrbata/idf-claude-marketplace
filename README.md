# IDF — Claude Code Marketplace for ESP-IDF Development

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin marketplace with tools for ESP-IDF development.

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
│   └── marketplace.json          ← Marketplace catalog
├── plugins/
│   └── idf/
│       ├── .claude-plugin/
│       │   └── plugin.json       ← Plugin manifest
│       ├── commands/
│       │   ├── review-branch.md  ← Review changes between branches (pre-MR/PR)
│       │   ├── review-changes.md ← Review staged + unstaged changes
│       │   ├── review-mr.md     ← Review a MR/PR by URL
│       │   ├── review-staged.md  ← Review only staged changes
│       └── CLAUDE.md
├── README.md
└── .gitignore
```

## Plugins

### idf

Commands for ESP-IDF code review.

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

## Requirements

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
- `git`
- `gh` (GitHub CLI) — for reviewing GitHub pull requests
- `glab` (GitLab CLI) — for reviewing GitLab merge requests

## License

MIT
