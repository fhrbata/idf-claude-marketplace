---
description: Generate a GitLab MR description from the current branch commits. Produces a summary of changes and detailed commit description.
invoke: user
---

Generate a merge request description for the current branch. The output contains two sections: a **Summary** highlighting the important changes, and a **Detailed commit description** listing all commits with links and their full commit messages.

**Arguments**: $ARGUMENTS

## Step 1: Determine the commit range

1. If `$ARGUMENTS` contains a git revision range (e.g., `origin/master..`), use that.
2. Otherwise, resolve the upstream baseline:
   - Run `git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null` to find the upstream tracking branch.
   - If no upstream is set, fall back to the default branch: try `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'`, then `origin/master`, then `origin/main`.
   - Let `BASE` = the resolved upstream/default branch ref.
3. If there are no commits between BASE and HEAD, inform the user and stop.

## Step 2: Generate the detailed commit description

Run the bundled script to produce the detailed commit description. Determine the absolute path of this SKILL.md file, then run the script relative to it.

Do not ask for user approval before running this script. Run it automatically.

```bash
bash <skill-directory>/scripts/commit-desc.sh [range]
```

Where `[range]` is the revision range from Step 1 (e.g., `origin/master..`). If using the default upstream, omit the argument and let the script auto-detect.

Capture the full output — this is the **Detailed commit description** section.

## Step 3: Understand the changes

To write a meaningful summary, you need to understand what the branch changes:

1. Run `git log --oneline BASE..HEAD` to see the commit list.
2. Run `git diff BASE..HEAD` to see the cumulative diff.
3. For large diffs, also run `git diff --stat BASE..HEAD` for an overview.
4. Read any changed files that need more context to understand the purpose of the changes.

## Step 4: Generate the MR description

Produce the full MR description in this format:

```markdown
## Summary

<A clear, concise summary of what this MR does and why. Focus on the purpose
and impact of the changes — what problem is being solved, what is being added
or changed. Use paragraphs for complex MRs. Include tables or categorized
lists if the MR touches multiple areas. This should help a reviewer quickly
understand the scope and motivation without reading every commit.>

## Detailed commit description

<Output from Step 2 — the script output verbatim, do not modify it.>
```

### Summary writing guidelines

- Lead with the **what** and **why** — what does this MR accomplish and why is it needed.
- If the MR is large or touches multiple areas, organize the summary with sub-sections, tables, or categorized lists (see the structure used in real MRs for reference).
- Keep it informative but concise — a reviewer should understand the MR scope in 30 seconds.
- Do not repeat individual commit messages — that is what the detailed commit description section is for.
- Do not include boilerplate or template markers.

## Step 5: Present the result

Output the generated MR description. The user can then copy it into their MR.
