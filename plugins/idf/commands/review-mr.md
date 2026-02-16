Review a merge request (GitLab) or pull request (GitHub) by URL.

**URL**: $ARGUMENTS

## Instructions

1. **Parse the URL** provided in `$ARGUMENTS` to determine the platform and extract identifiers:
   - **GitHub**: URL matches `github.com/<owner>/<repo>/pull/<number>` — use `gh` CLI.
   - **GitLab**: URL matches `gitlab.com/.../-/merge_requests/<number>` or a self-hosted GitLab instance — use `glab` CLI.
   - If the URL does not match either pattern, inform the user and stop.

2. **Fetch MR/PR metadata and diff**:
   - For GitHub:
     ```
     gh pr view <number> --repo <owner>/<repo> --json title,body,baseRefName,headRefName,files,additions,deletions
     gh pr diff <number> --repo <owner>/<repo>
     ```
   - For GitLab:
     ```
     glab mr view <number> --repo <owner>/<repo>
     glab mr diff <number> --repo <owner>/<repo>
     ```
   - If the CLI tool is not installed, inform the user which tool they need (`gh` or `glab`) and how to install it.

3. **Analyze the diff** thoroughly. For large MRs, focus on the most impactful changes first.

4. **Read source files** from the target branch when you need more context to understand a change — do not review the diff in isolation.

5. Provide a thorough code review organized by file, covering:

### Review Criteria

- **Correctness**: Logic errors, off-by-one errors, null/undefined handling, edge cases, race conditions.
- **Security**: Injection vulnerabilities (SQL, XSS, command), hardcoded secrets, insecure defaults, improper input validation.
- **Performance**: Unnecessary allocations, O(n²) where O(n) is possible, missing indexes, N+1 queries, blocking calls in async contexts.
- **Error Handling**: Swallowed exceptions, missing error paths, unhelpful error messages, resource leaks.
- **Readability**: Unclear naming, overly complex logic, missing context for non-obvious code.
- **Best Practices**: Framework/language idioms, deprecated API usage, missing tests for new logic.
- **MR Quality**: Commit message clarity, appropriate scope (not too large), test coverage for new code.

### Output Format

Start with a **MR Overview**:
- Title and description summary
- Base branch ← Head branch
- Files changed / lines added / lines removed

Then for each issue found, report:
- **File and line range**
- **Severity**: critical / warning / suggestion / nitpick
- **Category**: (from the criteria above)
- **Description**: What the problem is and why it matters
- **Suggestion**: How to fix it (with a code snippet when helpful)

End with a **Summary** section listing:
- Total issues by severity
- Overall assessment (approve / approve with suggestions / request changes)
- Top 3 most important items to address
