---
description: Review code changes — local branch changes (no args) or a GitHub PR / GitLab MR (pass URL). Offers to post draft review comments for MRs/PRs.
invoke: user
---

Review code changes. Without arguments, reviews all local changes on the current branch (working tree + staged + unpushed commits vs upstream). With a GitHub PR or GitLab MR URL, fetches and reviews that MR/PR, then offers to post draft review comments.

**Arguments**: $ARGUMENTS

## Mode Selection

- If `$ARGUMENTS` is empty, use **Local Mode**.
- If `$ARGUMENTS` contains a GitHub or GitLab URL, use **MR/PR Mode**.
- Otherwise, inform the user and stop.

---

## Local Mode

### Gather Changes

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

4. Continue to **Review** below.

---

## MR/PR Mode

### Fetch MR/PR Data

1. **Parse the URL** to determine the platform and extract identifiers:
   - **GitHub**: URL matches `github.com/<owner>/<repo>/pull/<number>` — use `gh` CLI.
   - **GitLab**: URL matches `gitlab.com/.../-/merge_requests/<number>` or a self-hosted GitLab instance — use `glab` CLI.
   - If the URL does not match either pattern, inform the user and stop.
   - If the CLI tool is not installed, inform the user which tool they need (`gh` or `glab`) and how to install it.

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

3. Continue to **Review** below.

---

## Review

### Review Methodology

1. **Understand the purpose first** — Read description/commits before code. Understand what the author claims to have done and why.
2. **Read all changed files in full** — Not just the diff. Understand surrounding context, function signatures, naming conventions, existing patterns. For very large diffs (more than 20 files changed), process in batches and prioritize the most impactful changes.
3. **Verify description claims against code** — If description says "migrated X to Y", check every instance. If it claims "config Z is defined in component W", verify. Discrepancies between stated intent and actual code are high-value findings.
4. **Check cross-file consistency** — When the same pattern appears in multiple changed files, systematically compare: naming, parameters, error handling, comments. Inconsistencies are common and impactful.
5. **Compare parallel implementations** — If the change modifies multiple implementations of the same concept (e.g., v1 and v2, different backends), compare for behavioral parity. Document differences and verify they are intentional.
6. **Trace edge cases** — For new/modified functions, consider all parameter values: empty lists, duplicate calls, invalid types, boundary values.
7. **Check documentation accuracy** — Verify comments/docstrings match actual behavior. Check for imprecise wording, stale comments, claims that are technically incorrect.

### Review Criteria

- **Correctness** — Logic errors, edge cases, off-by-one, null handling, race conditions.
- **Consistency** — Naming, behavior, API symmetry across files and implementations. Same concept should use same names. Parallel implementations should have equivalent behavior or documented differences.
- **Migration correctness** — When replacing a lenient operation with a stricter one, verify existing arguments are actually valid. Don't assume correctness because the old code "worked."
- **Error handling** — Missing error paths, swallowed errors, resource leaks, unclear error messages.
- **Documentation accuracy** — Comments match behavior, precise wording, no stale comments.
- **Security** — Hardcoded secrets, insecure defaults, improper input validation.
- **Performance** — Unnecessary allocations, algorithmic complexity, blocking calls.
- **Best practices** — Framework/language idioms, deprecated APIs, missing tests for new logic.

Additionally consider:
- Whether the commits tell a coherent story
- Whether uncommitted changes are consistent with the committed work (local mode)
- Whether the scope is appropriate for a single MR/PR
- Whether the changes are complete (no half-finished features, no leftover debug code)
- **MR Quality** (MR/PR mode): commit message clarity, appropriate scope, test coverage for new code

### Output Format

Start with an **Overview**:
- **Local mode**: current branch → upstream branch, unpushed commits count, staged/unstaged file counts, brief summary
- **MR/PR mode**: title and description summary, base ← head branch, files changed / lines added / lines removed

Then for each issue found, present as a numbered list:

```
### 1. [severity] file:line
**Category**: ...
**Description**: What the problem is and why it matters
**Suggestion**: How to fix it (with a code snippet when helpful)
```

End with a **Summary** section listing:
- Total issues by severity
- Overall assessment (ready to submit / needs minor fixes / needs significant work)
- Top 3 most important items to address

---

## Draft Review Comments (MR/PR mode only)

After presenting findings, offer to post them as draft review comments:
- Ask: "Would you like me to post these as draft review comments on the MR/PR?"
- If the user declines, stop.

**Let the user select comments to post**. They can:
- **Approve all**: "approve" or "go ahead"
- **Approve specific ones**: "approve 1, 3, 5"
- **Edit a comment**: "edit 2: change the message to ..."
- **Remove a comment**: "remove 4"
- **Reject all**: "reject" or "cancel"

Wait for the user's response before proceeding.

**Create the draft comments** using the platform-specific instructions below, then report results. Remind the user to review the drafts on the MR/PR page and submit the review themselves.

### GitHub: Creating a Pending Review

Create a single pending review containing all approved inline comments in one API call. Write a JSON file:

```json
{
  "event": "PENDING",
  "body": "",
  "comments": [
    {
      "path": "<file_path>",
      "line": <line_number>,
      "body": "<comment text>"
    }
  ]
}
```

Then create the review:
```
gh api repos/<owner>/<repo>/pulls/<number>/reviews --method POST --input <json_file>
```

**Line numbers**: `line` is the line number in the **new version** of the file (for added or context lines). For comments spanning multiple lines, add `start_line` for the first line and `line` for the last line. Use `side: "RIGHT"` (new file, default) or `side: "LEFT"` (deleted lines).

**General comments** (not tied to a specific line): include them in the review `body` field rather than in the `comments` array.

### GitLab: Creating Draft Notes

**Resolve the project ID** (needed for API calls):
- URL-encode the project path (replace `/` with `%2F`).
- Fetch the numeric ID:
  ```
  glab api "projects/<url_encoded_path>" | jq -r '.id'
  ```

**Fetch MR version SHAs** (needed for inline draft comments):
```
glab api "projects/<project_id>/merge_requests/<mr_iid>/versions" | jq '.[0]'
```
Use the latest version's `base_commit_sha`, `start_commit_sha`, and `head_commit_sha`.

**Create draft comments** on the MR:

IMPORTANT: For ALL draft comments (both general and inline), you MUST write a JSON file and use `--input` with `-H "Content-Type: application/json"`. The `-f` flag does NOT support nested fields like `position` and will silently produce broken comments.

- For **general draft comments** (not tied to a specific line), write a JSON file:
  ```json
  {
    "note": "<comment text>"
  }
  ```
  Then create the draft:
  ```
  glab api --method POST "projects/<project_id>/merge_requests/<mr_iid>/draft_notes" \
    --input <json_file> -H "Content-Type: application/json"
  ```

- For **inline draft comments** (tied to a specific file and line in the diff), write a JSON file:
  ```json
  {
    "note": "<comment text>",
    "position": {
      "base_sha": "<base_commit_sha>",
      "start_sha": "<start_commit_sha>",
      "head_sha": "<head_commit_sha>",
      "position_type": "text",
      "new_path": "<file_path>",
      "new_line": <line_number_integer>
    }
  }
  ```
  Then create the draft:
  ```
  glab api --method POST "projects/<project_id>/merge_requests/<mr_iid>/draft_notes" \
    --input <json_file> -H "Content-Type: application/json"
  ```

**Line number**: `new_line` must be a line number that appears in the **new side** of the diff (a context line or an added `+` line). Use `old_line` instead for removed `-` lines. The line number must correspond to a line visible in the diff, otherwise GitLab will reject the position.

**Tip**: Write multiple JSON files in parallel, then create the drafts in parallel for efficiency.

### Draft Comment Adjustments (on user request)

If the user asks to update or remove draft comments after they've been created:

**GitHub**:
- **Delete a pending review**:
  ```
  gh api repos/<owner>/<repo>/pulls/<number>/reviews/<review_id> --method DELETE
  ```
  Note: Individual comments within a pending review cannot be edited via API. Delete the review and recreate it.

**GitLab**:
- **Update a draft**:
  ```
  glab api --method PUT "projects/<project_id>/merge_requests/<mr_iid>/draft_notes/<note_id>" \
    -f note="<updated_comment>"
  ```
- **Delete a draft**:
  ```
  glab api --method DELETE "projects/<project_id>/merge_requests/<mr_iid>/draft_notes/<note_id>"
  ```
- **List current drafts** (to find note IDs):
  ```
  glab api "projects/<project_id>/merge_requests/<mr_iid>/draft_notes"
  ```

---

## Allowed CLI Usage

You may ONLY use `gh` and `glab` for the operations listed in this skill. Any other usage is strictly forbidden.

**Read operations**:
- `gh pr view`, `gh pr diff` — fetch PR data
- `gh api repos/<owner>/<repo>/pulls/<number>/reviews` — list reviews
- `glab mr view`, `glab mr diff` — fetch MR data
- `glab api "projects/<id>/merge_requests/<iid>/versions"` — fetch MR versions
- `glab api "projects/<id>/merge_requests/<iid>/draft_notes"` — list draft notes
- `glab api "projects/<url_encoded_path>"` — resolve project ID

**NEVER use gh/glab for**: merge, close, reopen, approve, revoke, publish, bulk_publish, or any operation outside of draft comment management.

## CLI Notes

### glab
- **No `--jq` flag**: glab does not support `--jq`. Pipe output through `jq` instead.
- **No `--hostname` flag for `glab api`**: glab resolves the GitLab host from its config file (`~/.config/glab-cli/config.yml`). Do NOT pass `--hostname` to `glab api`.
- **Nested JSON fields**: The `-f` flag creates flat key-value string parameters. It does NOT support nested field syntax like `-f "position[base_sha]=..."`. For nested JSON, you MUST use `--input` with a JSON file and `-H "Content-Type: application/json"`.
- Always URL-encode the project path when using `glab api` (replace `/` with `%2F`).

## General Notes

- Draft comments / pending reviews are only visible to you until you submit the review on the MR/PR page.
- Prefix each comment with a severity tag like `**[suggestion]**` or `**[critical]**` so the author can prioritize.
- For large MRs, focus on the most impactful issues. Aim for quality over quantity.
