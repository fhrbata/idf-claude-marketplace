#!/usr/bin/env bash
# Generate detailed commit description in markdown format.
#
# Produces a markdown list of commits with links to the remote repository.
# Each entry shows the commit subject as a clickable link followed by the
# indented commit body (Signed-off-by lines are stripped).
#
# Usage: commit-desc.sh [range]
#   range  Git revision range (default: <upstream>..)
#
# Git config:
#   mr.https-port  Optional HTTPS port for the remote URL

set -euo pipefail

range="${1:-}"

# Resolve upstream branch if no range given
if [ -z "$range" ]; then
    upstream=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
    if [ -z "$upstream" ]; then
        # Try default branch
        default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/@@' || true)
        if [ -z "$default" ]; then
            if git rev-parse --verify origin/master &>/dev/null; then
                default="origin/master"
            elif git rev-parse --verify origin/main &>/dev/null; then
                default="origin/main"
            else
                echo "Error: could not determine upstream branch" >&2
                exit 1
            fi
        fi
        upstream="$default"
    fi
    range="${upstream}.."
fi

# Convert remote URL to HTTPS for commit links
remote_url=$(git remote get-url origin | sed \
    -e 's|^ssh://[^@]*@\([^:/]*\):[0-9]*/|https://\1/|' \
    -e 's|^ssh://[^@]*@\([^:/]*\)/|https://\1/|' \
    -e 's|git@\([^:]*\):|https://\1/|' \
    -e 's|\.git$||')

port=$(git config mr.https-port 2>/dev/null || true)
if [ -n "$port" ]; then
    remote_url=$(echo "$remote_url" | sed "s|^https://\([^/]*\)|https://\1:${port}|")
fi

# Generate markdown commit list
git log --reverse --format="* [%s](${remote_url}/-/commit/%H)%n%n%b" "$range" \
    | sed -e '/^Signed-off-by:/d' -e '/^\*/!s/^/    /'
