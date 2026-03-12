---
description: Review all local changes on the current branch — working tree, staged, and unpushed commits vs upstream.
invoke: user
---

Review all local changes on the current branch that are not yet upstream — uncommitted changes (working tree + staged) and unpushed commits.

## Instructions

1. **Determine the upstream baseline**:
   - Run `git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null` to find the upstream tracking branch.
   - If no upstream is set, fall back to the default branch: try `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'`, then `main`, then `master`.
   - Let `BASE` = the resolved upstream/default branch ref.

2. **Gather all changes** (run in parallel where possible):
   - `git diff` — unstaged working tree changes
   - `git diff --staged` — staged changes
   - `git log --oneline BASE..HEAD` — unpushed commits
   - `git diff BASE..HEAD` — cumulative diff of unpushed commits
   - `git diff --stat BASE..HEAD` — summary of unpushed commit changes

3. **Assess what needs reviewing**:
   - If there are no changes at all (no working tree changes, no staged changes, no unpushed commits), inform the user and stop.
   - Report what was found: N unpushed commits, staged changes in M files, unstaged changes in K files.

4. **Read source files** in full for each changed file to understand surrounding context — do not review diffs in isolation. For very large diffs (more than 20 files changed), process in batches and prioritize the most impactful changes.

5. **Analyze all changes** following the Review Methodology and Review Criteria from the plugin guide (see `CLAUDE.md`). Additionally consider:
   - Whether the commits tell a coherent story
   - Whether uncommitted changes are consistent with the committed work
   - Whether the scope is appropriate for a single MR/PR
   - Whether the changes are complete (no half-finished features, no leftover debug code)

### Output Format

Start with a **Change Overview**:
- Current branch → upstream branch
- Unpushed commits: N
- Staged changes: M files
- Unstaged changes: K files
- Brief summary of what the changes accomplish

Then for each issue found, report:
- **File and line range**
- **Severity**: critical / warning / suggestion / nitpick
- **Category**: (from the criteria above)
- **Description**: What the problem is and why it matters
- **Suggestion**: How to fix it (with a code snippet when helpful)

End with a **Summary** section listing:
- Total issues by severity
- Overall assessment (ready to submit / needs minor fixes / needs significant work)
- Top 3 most important items to address
