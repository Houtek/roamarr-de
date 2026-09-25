#!/bin/sh
# Turn a pristine upstream checkout German, in place. Order matters:
#   1. code patches (patches/*.patch), applied to PRISTINE upstream so a moved line fails loudly
#   2. nav-label coverage check
#   3. the text table (de.json), with its structural self-check
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
