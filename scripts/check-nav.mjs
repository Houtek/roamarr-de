// Fail if a navigation label in the (patched) upstream source has no German display name in navDe.ts.
// Usage: node scripts/check-nav.mjs <upstream-dir>
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.argv[2];
const src = (p) => readFileSync(join(root, 'src', p), 'utf8');
const navDe = src('lib/navDe.ts');
const known = new Set([...navDe.matchAll(/^\s*(?:'([^']+)'|([A-Za-z]+)):\s*'/gm)].map((m) => m[1] ?? m[2]));

const missing = [];
for (const file of ['routes/+layout.svelte', 'lib/components/ProfileTabs.svelte']) {
	for (const m of src(file).matchAll(/\blabel:\s*'([^']+)'/g)) {
		if (!known.has(m[1])) missing.push(`${file}: ${m[1]}`);
	}
}
if (missing.length) {
	console.error(`nav labels without a German name in src/lib/navDe.ts (patches/0001-nav-labels.patch):\n  ${missing.join('\n  ')}`);
	process.exit(1);
}
console.error(`nav labels: all ${known.size} mapped`);
