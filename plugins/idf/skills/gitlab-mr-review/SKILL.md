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
- `glab api "projects/<url_encoded_path>" --jq '.id'`

**Write operations** (for managing draft comments only, and ONLY after user approval):
- `glab api --method POST "projects/<id>/merge_requests/<iid>/draft_notes" ...` — create a draft comment
- `glab api --method PUT "projects/<id>/merge_requests/<iid>/draft_notes/<note_id>" ...` — update a draft comment
- `glab api --method DELETE "projects/<id>/merge_requests/<iid>/draft_notes/<note_id>"` — delete a draft comment

**NEVER use glab for**: merge, close, reopen, approve, revoke, publish, bulk_publish, or any operation outside of draft_notes management.

## Instructions

### Phase 1: Fetch and Review

1. **Parse the URL** from `$ARGUMENTS`:
   - Extract the project path and MR number from the GitLab URL (e.g., `gitlab.espressif.cn/group/project/-/merge_requests/123`).
   - If the URL doesn't match a GitLab MR pattern, inform the user and stop.

2. **Resolve the project ID** (needed for API calls):
   - URL-encode the project path (replace `/` with `%2F`).
   - Fetch the numeric ID:
     ```
     glab api "projects/<url_encoded_path>" --jq '.id'
     ```

3. **Fetch MR metadata and diff**:
   ```
   glab mr view <number> --repo <owner>/<repo>
   glab mr diff <number> --repo <owner>/<repo>
   ```

4. **Read source files** from the target branch when you need more context — do not review the diff in isolation.

5. **Analyze the diff** using these criteria:
   - **Correctness**: Logic errors, off-by-one, null handling, edge cases, race conditions.
   - **Security**: Injection vulnerabilities, hardcoded secrets, insecure defaults.
   - **Performance**: Unnecessary allocations, algorithmic complexity, blocking calls.
   - **Error Handling**: Swallowed exceptions, missing error paths, resource leaks.
   - **Readability**: Unclear naming, overly complex logic.
   - **Best Practices**: Framework/language idioms, deprecated APIs, missing tests.

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
   glab api "projects/<project_id>/merge_requests/<mr_iid>/versions"
   ```
   Use the latest version's `base_commit_sha`, `start_commit_sha`, and `head_commit_sha`.

9. **Create approved draft comments** on the MR:

   - For **general draft comments** (not tied to a specific line):
     ```
     glab api --method POST "projects/<project_id>/merge_requests/<mr_iid>/draft_notes" \
       -f note="<comment>"
     ```

   - For **inline draft comments** (tied to a specific file and line in the diff):
     ```
     glab api --method POST "projects/<project_id>/merge_requests/<mr_iid>/draft_notes" \
       -f note="<comment>" \
       -f "position[base_sha]=<base_sha>" \
       -f "position[start_sha]=<start_sha>" \
       -f "position[head_sha]=<head_sha>" \
       -f "position[position_type]=text" \
       -f "position[new_path]=<file_path>" \
       -f "position[new_line]=<line_number>"
     ```

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
