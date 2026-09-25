#!/bin/sh
# Regenerate one patch of the series from its generator in patches/src/.
# Usage: scripts/regen-patch.sh <NNNN> <upstream-clone-to-copy-from> <scratch-dir>
#   NNNN        e.g. 0008 (needs patches/src/NNNN-*.py)
#   upstream    a local clone of visorcraft/Roamarr (any checkout; UPSTREAM_REF is checked out in a copy)
#   scratch-dir an empty/new directory to work in
set -eu
kit=$(cd "$(dirname "$0")/.." && pwd)
n=$1; upstream=$2; work=$3
gen=$(ls "$kit"/patches/src/"$n"-*.py)
name=$(basename "$gen" .py)
git clone -q "$upstream" "$work"
cd "$work"
git checkout -q --detach "$(cat "$kit/UPSTREAM_REF")"
for p in "$kit"/patches/*.patch; do
	[ "$(basename "$p" | cut -c1-4)" \< "$n" ] || continue
	git apply "$p"
done
git add -A
git -c user.name=regen -c user.email=regen@localhost commit -qm base --no-gpg-sign --allow-empty
(cd src && python3 "$gen")
git add -A
git diff --cached --output="$kit/patches/$name.patch"
echo "regenerated patches/$name.patch ($(git diff --cached --stat | tail -1))"
