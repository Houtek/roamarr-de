#!/bin/sh
# Turn a pristine upstream checkout German, in place. Order matters:
#   1. code patches (patches/*.patch), applied to PRISTINE upstream so a moved line fails loudly
#   2. nav-label coverage check
#   3. the text table (de.json), with its structural self-check
#   4. de.script.json: reviewed script literals (see scripts/apply-script.mjs)
#   5. de.templates.json: reviewed template literals (see scripts/templates.mjs)
# Usage: scripts/build-de.sh <upstream-dir>
set -eu
kit=$(cd "$(dirname "$0")/.." && pwd)
up=$1

for p in "$kit"/patches/*.patch; do
	[ -e "$p" ] || continue
	git -C "$up" apply --verbose "$p"
done
node "$kit/scripts/check-nav.mjs" "$up"
node "$kit/scripts/apply.mjs" "$up/src" "$kit/de.json"
# 4. reviewed display-only string literals in script code (atomic: all or nothing)
if [ -f "$kit/de.script.json" ]; then
	node "$kit/scripts/apply-script.mjs" "$up/src" "$kit/de.script.json"
fi
# 5. reviewed template literals with placeholders (atomic; placeholders may be reordered)
if [ -f "$kit/de.templates.json" ]; then
	node "$kit/scripts/templates.mjs" apply "$up/src" "$kit/de.templates.json"
fi
