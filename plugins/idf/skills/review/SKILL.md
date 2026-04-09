---
description: Thorough code review — committed changes on the current branch (no args) or a GitHub PR / GitLab MR (pass URL). Fetches base and head SHAs locally so the review has full file context, presents findings for discussion, then offers to post them as a draft pending review (GitHub) or draft notes (GitLab) with inline comments.
invoke: user
---

# Review

Review committed code changes thoroughly. The review always runs locally against a `BASE_SHA..HEAD_SHA` range using `git`, so you have the full contents of every changed file — and any related untouched files — not just the diff hunks. In Remote Mode (a GitHub PR or GitLab MR URL) the skill also fetches existing discussion threads so the output can surface unresolved reviewer asks.

**Arguments**: $ARGUMENTS

## Dispatch

- Empty `$ARGUMENTS` → **Local Mode**.
- URL whose path contains `/pull/<number>` → **Remote Mode (GitHub)**.
- URL whose path contains `/merge_requests/<number>` → **Remote Mode (GitLab)**. Works the same on `gitlab.com` and self-hosted instances — the path marker is the only signal, host doesn't matter.
- Anything else → tell the user the argument wasn't recognized and stop.

## Local Mode setup

Goal: resolve `BASE_SHA` (fork point with the default remote branch) and `HEAD_SHA` (current committed HEAD), then proceed to Review.

1. `HEAD_SHA = git rev-parse HEAD`.
2. Resolve the default remote branch to a concrete ref name. Try `git symbolic-ref --short refs/remotes/origin/HEAD` first (gives `origin/main` or `origin/master` as a name, not the symbolic ref itself); fall back to `origin/main` and `origin/master` directly if the symbolic ref isn't set. Call the result `BASE_REF`. If none of these exist, ask the user for a base ref (branch, tag, or SHA).
3. `BASE_SHA = git merge-base HEAD <BASE_REF>`.
4. **Confirm the base with the user before reviewing.** Non-default branching models (GitFlow, stacked release branches) can make the auto-detected base wrong, and the review is silently garbage if it's rooted at the wrong fork point. Tell them:
   > *"Reviewing against merge-base with `<BASE_REF>` (commit `<short SHA>`, N commits in range). If you intended a different base — e.g. a develop-style integration branch or a release branch — name it now; otherwise confirm to proceed."*
   
   If they name a different ref, recompute `BASE_SHA` with `git merge-base HEAD <new_ref>` and proceed.
5. If `BASE_SHA == HEAD_SHA`, stop — there's nothing committed to review on this branch.
6. **Warn about uncommitted changes.** If `git diff --quiet` or `git diff --staged --quiet` exits non-zero, tell the user the review will cover committed history only (`BASE_SHA..HEAD_SHA`) and confirm whether to continue. The review itself ignores the working tree and index; note the dirty state in the Overview so it's visible.
7. Proceed to **Review**.

## Remote Mode setup

Goal: resolve `BASE_SHA` and `HEAD_SHA` from the PR/MR, fetch both commits locally, fetch existing discussion threads, then proceed to Review.

1. **Pick the CLI**: `gh` for GitHub, `glab` for GitLab. If the relevant tool isn't installed, tell the user which to install and stop.
2. **Fetch PR/MR metadata** and extract the base and head SHAs. Capture stdout to a file and keep stderr separate so non-fatal warnings can't corrupt the JSON:
   
   **GitHub**:
   ```
   gh pr view <number> --repo <owner>/<repo> \
     --json title,body,author,labels,baseRefName,headRefName,baseRefOid,headRefOid,additions,deletions,files \
     2>/tmp/gh_stderr > /tmp/pr_meta.json
   ```
   Then `BASE_SHA = jq -r '.baseRefOid' /tmp/pr_meta.json` and `HEAD_SHA = jq -r '.headRefOid' /tmp/pr_meta.json`.
   
   **GitLab**:
   ```
   glab mr view <number> --repo <namespace>/<repo> --output json \
     2>/tmp/glab_stderr > /tmp/mr_meta.json
   ```
   Then:
   - `BASE_SHA = jq -r '.diff_refs.base_sha' /tmp/mr_meta.json`
   - `HEAD_SHA = jq -r '.diff_refs.head_sha' /tmp/mr_meta.json`
   - `PROJECT_ID = jq -r '.project_id' /tmp/mr_meta.json` — the numeric ID of the project the MR belongs to (the *target* project, which is also where discussions and draft notes live). For cross-fork MRs this is the upstream's project ID, not the source fork's — exactly what's needed for the rest of the flow. `project_id` is a standard top-level field in GitLab's MR API response, always present. No separate search / URL-encoded-path lookup needed.
3. **Fetch existing discussion threads** so the review can flag unresolved reviewer asks:
   
   **GitHub** — three endpoints:
   ```
   gh api repos/<owner>/<repo>/pulls/<number>/reviews   2>/tmp/gh_stderr > /tmp/reviews.json        # review bodies / verdicts
   gh api repos/<owner>/<repo>/pulls/<number>/comments  2>/tmp/gh_stderr > /tmp/line_comments.json  # inline review comments
   gh api repos/<owner>/<repo>/issues/<number>/comments 2>/tmp/gh_stderr > /tmp/pr_comments.json    # top-level PR comments
   ```
   
   **GitLab** — use the `PROJECT_ID` already extracted from the MR metadata in step 2. Discussions live on the target project, which is exactly what `.project_id` in the MR JSON points to (including for cross-fork MRs, where it's the upstream's ID, not the source fork's).
   ```
   glab api "projects/${PROJECT_ID}/merge_requests/<number>/discussions" \
     2>/tmp/glab_stderr > /tmp/discussions.json
   ```
   Keep `PROJECT_ID` in scope — it's also needed later if the user asks to post draft comments. If shell state has been discarded by then (e.g. between Bash tool calls), re-read it cheaply with `jq -r '.project_id' /tmp/mr_meta.json` — no extra API call.
4. **Fetch both commits into the local object store.** This step is also the "does my current working directory belong to this project?" check — if the fetch succeeds, the clone has everything the review needs; if it fails, it doesn't:
   ```
   git fetch origin <BASE_SHA> <HEAD_SHA>
   ```
   **If this fails, stop immediately and tell the user their current working directory is not a clone of the repository that the PR/MR targets.** Ask them to `cd` to the correct clone and re-run the skill. Do **not** try to locate the correct clone elsewhere on disk, do **not** add additional remotes, do **not** substitute `git -C <other_path>` for the rest of the flow — just fail cleanly with a clear message and let the user move. The fetch-based check is the single source of truth for "is this the right repo".
   
   **This deliberately does not check that the origin URL textually matches the PR/MR URL.** Mirrored setups (a project hosted canonically on one platform with a mirror on the other, multi-remote workflows, forks used as origin) all work as long as the commit SHAs exist on the origin remote, which is what the fetch actually verifies. Fork-based PRs on GitHub and GitLab also work without a fallback: both platforms advertise PR/MR heads via `refs/pull/<N>/head` / `refs/merge-requests/<N>/head` and enable reachable-SHA fetching, so the direct `git fetch origin <SHA>` resolves even when the SHA isn't on any branch.
5. **Recompute `BASE_SHA` as the real merge-base** of base and head:
   ```
   BASE_SHA=$(git merge-base <BASE_SHA> <HEAD_SHA>)
   ```
   Why: GitHub's `baseRefOid` is the current *tip* of the base branch, not the fork point of the PR. For a stale PR whose base has moved forward since the PR was opened, diffing against the base tip includes base-branch commits as apparent deletions — pure noise that drowns the real change. GitLab's `diff_refs.base_sha` is already the merge-base on well-behaved MRs, so this is a no-op for GitLab; done for symmetry and defense.
6. Proceed to **Review**.

## Review

You now have `BASE_SHA` and `HEAD_SHA`, both commits are in the local object store, and — in Remote Mode — metadata and discussion threads are on disk.

### Read the change with full context

- **Diff and stats** (redirect the diff to a file if large so it doesn't blow the Bash output buffer):
  ```
  git diff <BASE_SHA>..<HEAD_SHA> > /tmp/review_diff.patch
  git diff --stat <BASE_SHA>..<HEAD_SHA>
  git log --oneline <BASE_SHA>..<HEAD_SHA>
  ```
- **Read every changed file in full at the review head**, not just the diff hunks. This is the single biggest differentiator between a shallow review and a thorough one — cross-file inconsistencies, parity gaps, and migration drift are nearly impossible to catch from hunks alone:
  ```
  git show <HEAD_SHA>:<path>
  ```
  For files deleted in the range, read `git show <BASE_SHA>:<path>` instead (the path doesn't exist at HEAD). For renamed files (`R100 old new` in the diff), read both `<BASE_SHA>:<old>` and `<HEAD_SHA>:<new>`. Binary files can't be reviewed — note them in the Overview and skip.
- **Read outward from the changed files** in three directions, each finding a different class of bug:
  - **Siblings** — parallel copies of the same pattern elsewhere in the tree: v1/v2 implementations of the same feature, alternative backends behind a common interface, "we forked this once and now we have two copies that drift" situations, or naming drift between a legacy and a current prefix for the same subsystem. Siblings typically don't reference each other, so you can't follow a symbol to find them. Three mechanical discovery techniques, in increasing order of reliability:
    1. `git ls-files '**/<filename>'` — other copies of the changed file's filename elsewhere in the tree.
    2. `git grep -l '<shared naming prefix or suffix>'` — files whose exported symbols follow the same naming convention.
    3. `git grep -l '<shared lower-level primitive>'` — everyone who wraps the same underlying call the changed code wraps. Catches what the first two miss.
    
    When only one sibling is touched, explicitly check parity with the others.
  - **Callers** — consumers of the changed API. `git grep -l '<symbol>'` for direct textual callers, plus test files (which often exercise edge cases the production callers don't), plus any language-specific cross-reference tools available (ctags, `compile_commands.json` + clangd, LSP symbol search).
  - **Helpers** — the changed code's own dependencies. Walk the imports / `#include` / `REQUIRES` / `use` / `import` at the top of each changed file. If a helper's behavior is part of the change's contract, read the helper at `<HEAD_SHA>` too — helper changes that land in the same PR are a common source of silent behavior shifts.
- **Do not use `gh pr diff` or `glab mr diff`.** The local `git diff` is canonical: no truncation, no platform format quirks. The platform CLIs are only for metadata and discussions.

### Methodology (in order)

1. **Read the description and commit messages first.** Understand what the author claims to have done and why.
2. **Read project conventions** if present: `README`, `CONTRIBUTING`, `CLAUDE.md`, `.claude/`, `.github/copilot-instructions.md`, `.cursor/rules/`, language/framework style guides in the repo. Don't mention the absence of any of these in the final report.
3. **Read every changed file in full at `<HEAD_SHA>`.**
4. **Read outward** — siblings, callers, helpers.
5. **Verify description claims against the code.** Half-applied renames, "migrated all X" that missed a few, "removed Y" that left traces behind — this is the most common failure mode, and a high-value finding when caught.
6. **Trace edge cases** for new or modified functions: empty input, duplicate calls, invalid types, boundary values, concurrent access.
7. **Check documentation accuracy** — comments and docstrings should match actual behavior; no stale claims or imprecise wording.

### What to look for

- **Correctness** — logic errors, off-by-one, null/error handling, race conditions, resource leaks.
- **Consistency** — naming, behavior, and API symmetry across files and parallel implementations. Same concept should have the same name; parallel implementations should have equivalent behavior or documented differences.
- **Migration correctness** — when replacing a lenient operation with a stricter one, every previously valid input must still be valid.
- **Error handling** — missing error paths, swallowed errors, unclear messages.
- **Security** — hardcoded secrets, insecure defaults, missing input validation.
- **Performance** — unnecessary allocations, algorithmic complexity, blocking calls in hot paths.
- **Best practices** — framework/language idioms, deprecated APIs, missing tests for new logic.
- **Commit story** — coherent commits, appropriate scope for a single change, clear messages, no leftover debug code or half-finished features.
- **When the diff touches documentation**:
  - Prefer consistency with the existing page over applying stricter new rules to the changed lines.
  - Check that all examples in the same file are mutually consistent — migration guides and "before/after" sections commonly drift between an intermediate and a complete example.
  - When a compile-time flag, Kconfig symbol, or config key is replaced with a runtime option, check whether the **default behavior** changed and whether the changelog or migration guide calls it out.

### Present the findings

Produce a single structured message. Then **stop and wait for the user to discuss** — don't post anything to GitHub/GitLab yet, no matter how confident you are in the findings.

**Overview**
- **Mode**: `Local` / `GitHub PR #<n>` / `GitLab MR !<n>` (include the URL in Remote Mode).
- **Subject**: branch name (Local) or PR/MR title + author (Remote).
- **Range**: `<base short>..<head short>`, commit count, files changed, lines added/removed, binary files skipped. For Remote Mode, also `base ← head` branches. For Local Mode, `merge-base with <BASE_REF>` so the user can verify the base was chosen correctly.
- **Uncommitted work** (Local Mode only, only if the user opted to continue with a dirty tree): one line noting it's excluded from the review.

**Unresolved discussions** (Remote Mode only, *only if any exist*) — bullet list of reviewer asks from prior discussion threads that weren't addressed by later commits or a reply from the author. Quote each unresolved item verbatim (one short line) and note who asked. If all prior discussion is resolved, omit the section entirely — don't write "no unresolved discussions."

**Breaking changes** (*only if any exist*) — removed or renamed public APIs, changed behavior under existing flags, schema/config changes, dropped support matrices. Omit the section entirely if none.

**Findings** — numbered list. For each finding:
```
### N. [severity] file:line
**Category**: ...
**Description**: What the problem is and why it matters.
**Suggestion**: How to fix it (with a code snippet when helpful).
```

Severity tags:
- `[critical]` — must fix (bugs, security, data loss)
- `[issue]` — should fix (likely a bug or significant problem)
- `[suggestion]` — worth considering, not blocking
- `[nitpick]` — style, wording, or minor preference, optional

When referencing other code locations in a finding's Description or Suggestion body, use the same `file:line` (or `file:start-end`) format followed by a short quoted snippet of the actual lines, so the reader can identify the location without opening the file. Don't use `§N` or section-number shorthand.

**Summary** — total findings by severity, overall assessment (ready to submit / needs minor fixes / needs significant work), and the top items to address first.

## Discussion, then posting (Remote Mode only)

After the user reads the findings they may:
- Ask questions, challenge specific findings, or supply context you didn't have.
- Ask you to re-read particular files, check additional callers, or go deeper into a specific area.
- Approve a subset for posting and drop the rest.
- Edit the wording of individual comments before they go up.

**Do not post anything until the user explicitly tells you to.** When they do, confirm which findings to include (if they haven't specified) and then post them as a **draft** — never as a published review. The user submits the draft themselves from the PR/MR page after a final read-through.

### GitHub: pending review

Create a single pending review containing all approved inline comments in one API call. Write the JSON body to a file:

```json
{
  "body": "<optional top-level summary>",
  "comments": [
    {
      "path": "<file path>",
      "line": <line number in the new version of the file>,
      "side": "RIGHT",
      "body": "**[severity]** <comment text>"
    }
  ]
}
```

Then POST it:

```
gh api repos/<owner>/<repo>/pulls/<number>/reviews \
  --method POST --input /tmp/review.json \
  2>/tmp/gh_stderr > /tmp/gh_response.json
```

**Critical: do NOT include an `event` field in the JSON.** The GitHub API rejects `"event": "PENDING"` as invalid, and any other value (`APPROVE`, `COMMENT`, `REQUEST_CHANGES`) immediately *publishes* the review. Omitting the field is the only way to create a pending (draft) review via the API.

- `line` is the line number in the **new** version of the file (context lines or added `+` lines). Always pass `side: "RIGHT"` explicitly for new-version lines — it's the default if omitted, but being explicit removes any ambiguity for readers comparing POST bodies. For deleted-line comments, set `side: "LEFT"` instead. For multi-line comments, use `start_line` for the first line and `line` for the last.
- For general (not-line-specific) comments, put them in the top-level `body` rather than in the `comments` array.
- Individual comments in a pending review can't be edited via API after creation. If the user wants to change something, delete the whole pending review (`gh api repos/<owner>/<repo>/pulls/<number>/reviews/<id> --method DELETE`) and recreate.
- **Verify success via exit code + response `id` + `state: "PENDING"`, not via `line` / `side`.** For a freshly-created pending review, GitHub returns `line`, `side`, `start_line`, `start_side`, and `original_line` as `null` in the response — these only get populated after the review is submitted. The reliable success signals are: `gh api` exit code 0, a numeric `id` in the response, and `state: "PENDING"`. Don't treat the null position fields as an error. (This is analogous to the null-field behavior GitLab's `draft_notes` POST exhibits — see the GitLab section below.)
- **The response's `position` field is the 1-indexed diff-hunk offset, not the new-file line number.** For files *added* by the PR (where every new-version line is a `+` line), diff position and new-file line coincide — `position: 45` means line 45. For files *modified* by the PR, they don't — `position` counts context and deleted lines too, so a comment POSTed with `line: 100, side: "RIGHT"` may read back as `position: 67` or similar. GitHub stores the anchor correctly as long as the POST passed `line` + `side`; the asymmetric interpretation only affects how the response reads back. (Tested end-to-end so far only on a PR adding a brand-new file — modified-file behavior is unverified.)
- **Retry safety** (atomicity): unlike GitLab's per-comment `draft_notes` POSTs, the GitHub pending-review API creates the whole review in a single atomic call — either the entire review lands on the server or none of it does, so there's no partial-failure case to recover from mid-sequence. A simple retry is safe in most situations. But if the POST failed in a way where the outcome is ambiguous (network timeout mid-request, HTTP 5xx from the server, response body parse threw), list existing reviews (`gh api repos/<owner>/<repo>/pulls/<number>/reviews`) before retrying to avoid creating a second pending review.

### GitLab: draft notes

Each inline comment is a separate `POST .../draft_notes`. Before posting anything, fetch the MR's version SHAs — these anchor the comments to a specific diff version and are **distinct** from the review-range `BASE_SHA`/`HEAD_SHA`; don't reassign the review-range variables here:

```
glab api "projects/${PROJECT_ID}/merge_requests/<number>/versions" \
  2>/tmp/glab_stderr > /tmp/versions.json
```

The position SHAs for inline draft notes are `.[0].base_commit_sha`, `.[0].start_commit_sha`, and `.[0].head_commit_sha` from the versions file (latest version first). **On an MR with exactly one version** (no force-pushes, no extra pushes after the MR was opened), these position SHAs coincide exactly with the review-range `BASE_SHA` / `HEAD_SHA` — they look identical and the distinction seems cosmetic. On an MR with multiple versions they diverge. Treat them as distinct values regardless, so the same code works for both cases — do not reuse the review-range variables as if they were the position SHAs.

For each inline comment, compose the JSON body with `jq --rawfile`. The comment body is multi-line markdown (backticks, code fences, quoted excerpts, em-dashes, nested blockquotes) and embedding it as a JSON string literal by hand is a quoting nightmare. Write the markdown to a file first, then let jq do the encoding:

```bash
# 1. Write the comment body as plain markdown.
cat > /tmp/note.md <<'MARKDOWN_EOF'
**[severity]** <comment text with `backticks`, em-dashes, code blocks, etc.>
MARKDOWN_EOF

# 2. Build the JSON with jq --rawfile for the note body and
#    --arg / --argjson for the position fields (never hand-type them):
jq -n \
  --rawfile note /tmp/note.md \
  --arg base_sha  "<versions[0].base_commit_sha>" \
  --arg start_sha "<versions[0].start_commit_sha>" \
  --arg head_sha  "<versions[0].head_commit_sha>" \
  --arg new_path  "<file path>" \
  --argjson new_line <line number in the new version of the file> \
  '{
    note: $note,
    position: {
      base_sha: $base_sha,
      start_sha: $start_sha,
      head_sha: $head_sha,
      position_type: "text",
      new_path: $new_path,
      new_line: $new_line
    }
  }' > /tmp/note.json
```

The resulting JSON has the shape:

```json
{
  "note": "**[severity]** ...",
  "position": {
    "base_sha":  "<versions[0].base_commit_sha>",
    "start_sha": "<versions[0].start_commit_sha>",
    "head_sha":  "<versions[0].head_commit_sha>",
    "position_type": "text",
    "new_path": "<file path>",
    "new_line": <line number in the new version of the file>
  }
}
```

Then POST it:

```
glab api --method POST "projects/${PROJECT_ID}/merge_requests/<number>/draft_notes" \
  --input /tmp/note.json -H "Content-Type: application/json" \
  2>/tmp/glab_stderr > /tmp/glab_response.json
```

For general (not-line-specific) draft notes, omit the `position` object — just `{"note": "..."}`.

**Critical `glab` gotchas you will hit if you don't know about them**:

- **Always use `--input` with a JSON file for nested fields.** The `-f` flag creates flat string parameters and silently drops nested fields like `position[base_sha]`. If you use `-f` for a draft note with a position, the POST succeeds but the `position` is empty and the draft is broken.
- **Never pipe `glab api` into a JSON parser via `2>&1`.** glab writes non-fatal warnings to stderr (SSH `known_hosts` updates, config-file write failures under sandboxed filesystems). Mixed into stdout, they silently break JSON parsing *after* the POST has already succeeded on the server. Always redirect stdout to a file and stderr elsewhere (`2>/dev/null` or `2>/tmp/glab_stderr`); the exit code is the only reliable signal of whether the POST landed.
- **`draft_notes` POST is not idempotent.** If the response parse fails but the POST succeeded server-side, a naive retry creates a duplicate. Before retrying, list existing drafts (`glab api "projects/${PROJECT_ID}/merge_requests/<number>/draft_notes"`) and skip any that already match the new draft's `new_path` + `new_line` + opening line of `note`.
- **Create drafts sequentially**, not in parallel. Parallel creation amplifies the partial-failure problem and makes deduplication harder.
- **POST response for newly-created drafts has several `null` fields.** The response to a `POST .../draft_notes` returns `note_type: null`, `author: null`, `line_code: null`, and `resolvable: null` for a freshly-created draft — these only get populated once the review is submitted. Verify the POST succeeded by checking the command's exit code and the presence of a numeric `id` in the response, not by inspecting those fields.
- **No `--jq` flag on glab** — pipe to `jq` instead. **No `--hostname` for `glab api`** — the host comes from `~/.config/glab-cli/config.yml`.

**Line numbers**: `new_line` must be a line visible on the **new** side of the diff (a context line or a `+` added line). For comments on deleted lines, use `old_line` instead. The line must actually appear in the diff — GitLab rejects positions that point at lines outside the diff hunks.

**Adjusting drafts after posting**:
- Update a draft: `glab api --method PUT "projects/${PROJECT_ID}/merge_requests/<number>/draft_notes/<id>" -f note="<updated text>"` (`-f` works here because `note` is a flat field, not nested).
- Delete a draft: `glab api --method DELETE "projects/${PROJECT_ID}/merge_requests/<number>/draft_notes/<id>"`.
- List current drafts: `glab api "projects/${PROJECT_ID}/merge_requests/<number>/draft_notes"`.

### After posting

Report how many drafts were posted and on which files. Remind the user the review is still a **draft** — they need to submit it from the PR/MR page for the reviewers (and author) to see it.

## What `gh` and `glab` must never be used for

`gh` and `glab` are read-only for this skill with one exception: the draft-posting flow above. Never use them for:

- `merge`, `close`, `reopen`, `approve`, `revoke`, `publish`, `bulk_publish`
- `gh pr review --approve` / `--request-changes`, `gh pr merge`, `gh pr ready`
- `glab mr approve`, `glab mr merge`
- any other `gh api` / `glab api` write (`--method POST`/`PUT`/`DELETE`) outside the draft/pending flows above

For diffs, file contents, commit history, and anything else about the code itself, use local `git` only.
