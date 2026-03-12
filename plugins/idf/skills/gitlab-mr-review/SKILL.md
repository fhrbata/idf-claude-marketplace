---
description: Review a GitLab MR — analyze diff, create draft review comments, and update drafts on request. User submits the review on GitLab.
invoke: user
---

Review a GitLab merge request. Analyze the diff, create draft review comments on the MR, and update or remove drafts on request. The user reviews the drafts on the GitLab MR page and submits the review themselves.

**URL**: $ARGUMENTS

## Allowed glab usage

You may ONLY use glab for the operations listed below. Any other glab usage is strictly forbidden.

**Read operations** (for fetching MR data):
- `glab mr view <number> --repo <owner>/<repo>`
- `glab mr diff <number> --repo <owner>/<repo>`
- `glab api "projects/<id>/merge_requests/<iid>/versions"`
- `glab api "projects/<id>/merge_requests/<iid>/draft_notes"`
- `glab api "projects/<url_encoded_path>" | jq -r '.id'`

**Write operations** (for managing draft comments only, and ONLY after user approval):
- `glab api --method POST "projects/<id>/merge_requests/<iid>/draft_notes" --input <json_file> -H "Content-Type: application/json"` — create a draft comment
- `glab api --method PUT "projects/<id>/merge_requests/<iid>/draft_notes/<note_id>" -f note="<text>"` — update a draft comment
- `glab api --method DELETE "projects/<id>/merge_requests/<iid>/draft_notes/<note_id>"` — delete a draft comment

**NEVER use glab for**: merge, close, reopen, approve, revoke, publish, bulk_publish, or any operation outside of draft_notes management.

## Important: glab CLI notes

- **No `--jq` flag**: glab does not support `--jq`. Pipe output through `jq` instead:
  ```
  glab api "projects/<url_encoded_path>" | jq -r '.id'
  ```
- **No `--hostname` flag for `glab api`**: glab resolves the GitLab host from its config file (`~/.config/glab-cli/config.yml`). Do NOT pass `--hostname` to `glab api`. The `--hostname` flag is only for `glab mr` subcommands if needed, but typically the configured host is sufficient.
- **Nested JSON fields**: The `-f` flag creates flat key-value string parameters. It does NOT support nested field syntax like `-f "position[base_sha]=..."`. For nested JSON (e.g., draft note positions), you MUST use `--input` with a JSON file and `-H "Content-Type: application/json"`. See Phase 3 for the exact pattern.

## Instructions

### Phase 1: Fetch and Review

1. **Parse the URL** from `$ARGUMENTS`:
   - Extract the project path and MR number from the GitLab URL (e.g., `gitlab.espressif.cn/group/project/-/merge_requests/123`).
   - If the URL doesn't match a GitLab MR pattern, inform the user and stop.

2. **Resolve the project ID** (needed for API calls):
   - URL-encode the project path (replace `/` with `%2F`).
   - Fetch the numeric ID by piping through `jq`:
     ```
     glab api "projects/<url_encoded_path>" | jq -r '.id'
     ```

3. **Fetch MR metadata and diff** (can be run in parallel):
   ```
   glab mr view <number> --repo <owner>/<repo>
   glab mr diff <number> --repo <owner>/<repo>
   ```

4. **Read source files** from the target branch when you need more context — do not review the diff in isolation.

5. **Analyze the diff** following the Review Methodology and Review Criteria from the plugin guide (see `CLAUDE.md`).

### Phase 2: Present Findings for Approval

6. **Present each proposed comment** in a numbered list:

   ```
   ## Proposed Draft Comments

   ### 1. [severity] file:line
   > The comment text that would be created as a draft note.

   ### 2. [severity] file:line (general)
   > A general comment not tied to a specific line.

   ...
   ```

7. **Ask the user** to review the proposed comments. They can:
   - **Approve all**: "approve" or "go ahead"
   - **Approve specific ones**: "approve 1, 3, 5"
   - **Edit a comment**: "edit 2: change the message to ..."
   - **Remove a comment**: "remove 4"
   - **Reject all**: "reject" or "cancel"

   Wait for the user's response before proceeding.

### Phase 3: Create Draft Comments

8. **Fetch MR version SHAs** (needed for inline draft comments):
   ```
   glab api "projects/<project_id>/merge_requests/<mr_iid>/versions" | jq '.[0]'
   ```
   Use the latest version's `base_commit_sha`, `start_commit_sha`, and `head_commit_sha`.

9. **Create approved draft comments** on the MR:

   IMPORTANT: For ALL draft comments (both general and inline), you MUST write a JSON file and use `--input` with `-H "Content-Type: application/json"`. The `-f` flag does NOT support nested fields like `position` and will silently produce broken comments that appear at the bottom of the MR instead of inline in the diff.

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

   **Tip**: You can write multiple JSON files in parallel (one per comment) and then create the drafts in parallel for efficiency.

10. **Report results**: List which draft comments were created successfully and note any failures. Remind the user to go to the MR page on GitLab to review the drafts and submit the review.

### Phase 4: Adjustments (on user request)

If the user asks to update or remove draft comments after they've been created:

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

## Notes

- Draft comments are only visible to you until you submit the review on the GitLab MR page.
- Prefix each draft comment with a severity tag like `**[suggestion]**` or `**[critical]**` so the MR author can prioritize after you submit.
- For large MRs, focus on the most impactful issues. Aim for quality over quantity.
- Always URL-encode the project path when using `glab api` (replace `/` with `%2F`).
