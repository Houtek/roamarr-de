// Compare two vitest JSON reports; exit 1 if any test fails in the patched run but not the baseline.
// Usage: node compare-tests.mjs <baseline.json> <patched.json>
import { readFileSync } from 'node:fs';

const failing = (path) => {
	const r = JSON.parse(readFileSync(path, 'utf8'));
	const out = new Set();
	for (const file of r.testResults ?? []) {
		const name = file.name.replace(/^.*?\/src\//, 'src/');
		for (const t of file.assertionResults ?? []) {
			if (t.status === 'failed') out.add(`${name} > ${t.fullName}`);
		}
	}
	return { out, total: r.numTotalTests };
};

const [bPath, pPath, expectedPath] = process.argv.slice(2);
const b = failing(bPath), p = failing(pPath);
// tests that assert English wording and are EXPECTED to fail once translated; one per line, # comments
const expected = new Set(
	expectedPath
		? readFileSync(expectedPath, 'utf8').split('\n').map((l) => l.replace(/#.*/, '').trim()).filter(Boolean)
		: []
);
const all = [...p.out].filter((t) => !b.out.has(t)).sort();
const introduced = all.filter((t) => !expected.has(t));
const allowed = all.filter((t) => expected.has(t));
if (allowed.length) console.log(`expected (asserts English wording): \n  ${allowed.join('\n  ')}`);
const fixed = [...b.out].filter((t) => !p.out.has(t)).sort();

console.log(`baseline: ${b.out.size} failing of ${b.total}`);
console.log(`patched:  ${p.out.size} failing of ${p.total}`);
if (fixed.length) console.log(`\nfailing only in baseline (flaky/env): \n  ${fixed.join('\n  ')}`);
if (introduced.length) {
	console.log(`\nINTRODUCED by the translation (${introduced.length}):\n  ${introduced.join('\n  ')}`);
	process.exit(1);
}
console.log('\nno test failures introduced by the translation');
