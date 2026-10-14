#!/usr/bin/env bash
# Link Claude Code config from this repo into ~/.claude.
# Safe to rerun. Existing real files are moved to <name>.bak.<timestamp>.
set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dst="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
stamp="$(date +%Y%m%d%H%M%S)"

link() {  # link <source> <target>
    local from="$1" to="$2"
    if [ -L "$to" ] && [ "$(readlink "$to")" = "$from" ]; then
        echo "ok      $to"; return
    fi
    if [ -e "$to" ] || [ -L "$to" ]; then
        mv "$to" "$to.bak.$stamp"; echo "backup  $to -> $to.bak.$stamp"
    fi
    ln -s "$from" "$to"; echo "linked  $to"
}

mkdir -p "$dst/skills"
link "$src/CLAUDE.md"     "$dst/CLAUDE.md"
link "$src/settings.json" "$dst/settings.json"

# Link each skill on its own. Claude Code manages other dirs in skills/ (synced, .trash).
for s in "$src"/skills/*/; do
    link "${s%/}" "$dst/skills/$(basename "$s")"
done
