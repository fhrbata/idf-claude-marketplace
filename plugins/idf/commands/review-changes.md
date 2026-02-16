Review all staged and unstaged changes on the current branch.

## Instructions

1. Run `git diff` to get unstaged changes and `git diff --staged` to get staged changes.
2. Run `git log --oneline -10` to understand recent commit context.
3. If there are no changes at all, inform the user and stop.
4. For each changed file, read the full file to understand the surrounding context — do not review the diff in isolation.
5. Provide a thorough code review organized by file, covering:

### Review Criteria

- **Correctness**: Logic errors, off-by-one errors, null/undefined handling, edge cases, race conditions.
- **Security**: Injection vulnerabilities (SQL, XSS, command), hardcoded secrets, insecure defaults, improper input validation.
- **Performance**: Unnecessary allocations, O(n²) where O(n) is possible, missing indexes, N+1 queries, blocking calls in async contexts.
- **Error Handling**: Swallowed exceptions, missing error paths, unhelpful error messages, resource leaks.
- **Readability**: Unclear naming, overly complex logic, missing context for non-obvious code.
- **Best Practices**: Framework/language idioms, deprecated API usage, missing tests for new logic.

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
