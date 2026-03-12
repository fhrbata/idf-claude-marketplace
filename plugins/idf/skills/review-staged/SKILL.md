---
description: Review only staged (git added) changes before committing.
invoke: user
---

Review only the staged changes (what would be included in the next commit).

## Instructions

1. Run `git diff --staged` to get staged changes.
2. Run `git log --oneline -10` to understand recent commit context.
3. If there are no staged changes, inform the user and stop.
4. For each changed file, read the full file to understand the surrounding context — do not review the diff in isolation.
5. Provide a thorough code review organized by file, following the Review Methodology and Review Criteria from the plugin guide (see `CLAUDE.md`).

### Output Format

For each issue found, report:
- **File and line range**
- **Severity**: critical / warning / suggestion / nitpick
- **Category**: (from the criteria above)
- **Description**: What the problem is and why it matters
- **Suggestion**: How to fix it (with a code snippet when helpful)

End with a **Summary** section listing:
- Total issues by severity
- Overall assessment (approve / approve with suggestions / request changes)
- Top 3 most important items to address
