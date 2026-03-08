---
description: Generate a weekly status report from GitHub and GitLab activity. Use when the user asks for a status report, weekly summary, or activity report.
invoke: user
---

# Status Report

Generate a combined weekly status report from GitHub and GitLab activity.

## Step 1: Collect activity data

Run the data collection script. It fetches events from GitHub and GitLab and writes them to a JSON file.

Determine the absolute path of this SKILL.md file, then run `scripts/report.py` relative to it.

Do not ask for user approval before running this script. Run it automatically.

```bash
python <skill-directory>/scripts/report.py
```

Optional: if the user specifies how many days to look back:

```bash
python <skill-directory>/scripts/report.py --days 14
```

The script prints the path to the output JSON file on stdout. The file contains all GitHub and GitLab activity events.

## Step 2: Read the activity data and generate the report

Read the ENTIRE JSON file produced by step 1 using the file read tool (not the terminal).
The file can be large — you MUST read all of it to produce a complete report.

Then write a weekly status report following these rules:

### Writing style
- Describe the work in your own words — what was done, what problem was solved, why it matters.
- Use MR/PR/issue IDs only as parenthetical references for traceability.
- Keep entries short: 1 line for simple items, 2-3 lines for complex ones.
- GOOD: "Fixed a race condition in the Wi-Fi reconnect logic that caused intermittent drops on multi-core targets (MR !312). (AI saved ~1-2h)"
- BAD: "MR !312 - fix: wifi reconnect race condition on multi-core targets"

### Sections
Use exactly these three sections:

1. **Authored MRs/PRs** — MRs/PRs the user created or owns (pushed commits to their own branch). Repeated pushes to the same branch are typically rebases, not new work — ignore push counts.
2. **Code Reviews** — MRs/PRs opened by OTHER users where this user left review comments, approved, or requested changes. Events like PullRequestReviewEvent or comment-only activity on other people's MRs/PRs always go here, never under Authored.
3. **Other Activity** — Everything else (issue comments, branch creation, project joins, etc.). One-liner bullets only.

### AI usage
The user uses AI tools continuously for all work. Add an inline "(AI saved ~Xh)" note ONLY for non-trivial tasks where AI meaningfully helped (complex code, debugging, research). Skip it for trivial items. At the end, add: "Total estimated AI time saved this week: ~X-Yh" (sum of inline notes only).

### Length
The entire report must not exceed 3500 characters. Shorten descriptions if needed — never truncate mid-sentence. Every item must be present. No preamble, sign-offs, or decorative separators.

## Configuration

Settings are loaded from a config file (`[status-report]` section), and can be overridden by environment variables (env vars take precedence).

### Config file location

| Platform | Path |
|----------|------|
| Linux | `~/.config/idf-tools-cursor-skills/config.ini` |
| macOS | `~/Library/Application Support/idf-tools-cursor-skills/config.ini` |
| Windows | `%APPDATA%\idf-tools-cursor-skills\config.ini` |

Or set `IDF_TOOLS_SKILLS_CONFIG` env var to use a custom path.

### Settings

| Config key | Env variable | Description |
|------------|--------------|-------------|
| `gitlab_url` | `GITLAB_URL` | GitLab instance URL |
| `gitlab_token` | `GITLAB_TOKEN` | GitLab personal access token |
| `gitlab_user` | `GITLAB_USER` | GitLab username |
| `github_user` | `GITHUB_USER` | GitHub username |
| `days_back` | `DAYS_BACK` | Number of days to look back (default: `7`, can also use `--days` flag) |
