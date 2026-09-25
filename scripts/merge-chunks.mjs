// Validate translator chunk outputs and merge them into de.json.
// Usage: node scripts/merge-chunks.mjs <de.json> <chunkN.json> <chunkN.de.json> [<chunkM.json> <chunkM.de.json> ...]
// Hard errors (exit 1, nothing written): order/key mismatch, markup characters, entity drift, surrounding whitespace.
// Warnings (printed, merged anyway): formal address, trailing-colon drift, de identical to en.
// A null `de` means "leave English, needs a code patch" and is skipped, as are identical en/de pairs.
import { readFileSync, writeFileSync } from 'node:fs';

const [tablePath, ...pairs] = process.argv.slice(2);
const table = JSON.parse(readFileSync(tablePath, 'utf8'));
const entities = (s) => (s.match(/&[a-z]+;|&#\d+;/g) ?? []).sort().join(' ');
const errors = [], warnings = [], nulls = [];
let added = 0, identical = 0;

for (let i = 0; i < pairs.length; i += 2) {
	const input = JSON.parse(readFileSync(pairs[i], 'utf8'));
	const output = JSON.parse(readFileSync(pairs[i + 1], 'utf8'));
	const tag = pairs[i + 1].split('/').pop();
	if (input.length !== output.length) errors.push(`${tag}: ${output.length} entries, expected ${input.length}`);
	input.forEach((inp, j) => {
		const o = output[j];
		if (!o || o.en !== inp.en) return errors.push(`${tag}[${j}]: en mismatch (${JSON.stringify(o?.en)?.slice(0, 60)})`);
		if (o.de === null) return nulls.push(`${o.en}  —  ${o.note ?? ''}`);
		const de = o.de;
		if (typeof de !== 'string' || !de.length) return errors.push(`${tag}[${j}]: empty de for ${JSON.stringify(o.en)}`);
		if (/[{}<>]/.test(de)) errors.push(`${tag}[${j}]: markup char in ${JSON.stringify(de)}`);
		if (entities(de) !== entities(o.en)) errors.push(`${tag}[${j}]: entities ${entities(o.en)} -> ${entities(de)}`);
		if (de !== de.trim()) errors.push(`${tag}[${j}]: surrounding whitespace in ${JSON.stringify(de)}`);
		if (/(^|[.!?:]\s+|,\s*)(Sie|Ihr|Ihre|Ihnen|Ihren|Ihrem|Ihrer)\b/.test(de) || /\b(Ihnen|Ihrem|Ihren)\b/.test(de))
			warnings.push(`formal? ${o.en.slice(0, 50)} -> ${de.slice(0, 80)}`);
		if (o.en.endsWith(':') !== de.endsWith(':')) warnings.push(`colon drift: ${o.en.slice(0, 50)} -> ${de.slice(0, 50)}`);
		if (de === o.en) { identical++; return; }
		if (o.en in table && table[o.en] !== de) warnings.push(`overrides existing: ${o.en} (${table[o.en]} -> ${de})`);
		table[o.en] = de;
		added++;
	});
}

for (const w of warnings) console.log(`WARN  ${w}`);
console.log(`\nnull (needs code patch): ${nulls.length}`);
for (const n of nulls) console.log(`  ${n.slice(0, 160)}`);
if (errors.length) {
	for (const e of errors) console.log(`ERROR ${e}`);
	console.log(`\n${errors.length} error(s); de.json NOT written`);
	process.exit(1);
}
const sorted = Object.fromEntries(Object.entries(table).sort(([a], [b]) => a.localeCompare(b)));
writeFileSync(tablePath, JSON.stringify(sorted, null, 1) + '\n');
console.log(`\nmerged: +${added}, kept-English (identical): ${identical}, table size: ${Object.keys(sorted).length}`);
