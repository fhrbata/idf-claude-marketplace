Review changes between two branches before creating a merge request or pull request.

**Arguments**: $ARGUMENTS

## Instructions

1. **Determine the branches to compare**:
   - Parse `$ARGUMENTS` for branch names. Expected formats:
     - `<head-branch>` — compare `<head-branch>` against the default branch (auto-detect with `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'`, fall back to `main`, then `master`).
     - `<base-branch> <head-branch>` — compare `<head-branch>` against `<base-branch>`.
     - *(no arguments)* — compare the current branch (`HEAD`) against the default branch.
   - Verify both branches exist. If either is missing, inform the user and stop.

2. **Fetch branch metadata**:
   - Run `git log --oneline <base-branch>..<head-branch>` to list commits that will be part of the MR/PR.
   - Run `git diff --stat <base-branch>...<head-branch>` to get a summary of files changed, insertions, and deletions (triple-dot merge-base diff).
   - If there are no differences, inform the user that the branches are identical and stop.

3. **Get the full diff**:
   - Run `git diff <base-branch>...<head-branch>` to get the complete diff.
   - For very large diffs (more than 20 files changed), process files in batches and prioritize the most impactful changes.

4. **Read source files** from the head branch when you need more context to understand a change — do not review the diff in isolation. Use `git show <head-branch>:<file-path>` to read files from the head branch without checking it out.

5. **Analyze the diff** thoroughly. Consider:
   - Whether the commits tell a coherent story
   - Whether the scope is appropriate for a single MR/PR
   - Whether the changes are complete (no half-finished features, no leftover debug code)

6. Provide a thorough code review organized by file, covering:

### Review Criteria

- **Correctness**: Logic errors, off-by-one errors, null/undefined handling, edge cases, race conditions.
- **Security**: Injection vulnerabilities (SQL, XSS, command), hardcoded secrets, insecure defaults, improper input validation.
- **Performance**: Unnecessary allocations, O(n²) where O(n) is possible, missing indexes, N+1 queries, blocking calls in async contexts.
- **Error Handling**: Swallowed exceptions, missing error paths, unhelpful error messages, resource leaks.
- **Readability**: Unclear naming, overly complex logic, missing context for non-obvious code.
- **Best Practices**: Framework/language idioms, deprecated API usage, missing tests for new logic.
- **MR/PR Readiness**: Commit history quality, appropriate scope, test coverage, no leftover debug code or TODOs.

### Output Format

Start with a **Branch Comparison Overview**:
- Base branch ← Head branch
- Number of commits
- Files changed / lines added / lines removed
- Brief summary of what the changes accomplish (inferred from commits and diff)

Then for each issue found, report:
- **File and line range**
- **Severity**: critical / warning / suggestion / nitpick
- **Category**: (from the criteria above)
- **Description**: What the problem is and why it matters
- **Suggestion**: How to fix it (with a code snippet when helpful)

End with a **Summary** section listing:
- Total issues by severity
- Overall assessment (ready to submit / needs minor fixes / needs significant work)
- Top 3 most important items to address before submitting the MR/PR
