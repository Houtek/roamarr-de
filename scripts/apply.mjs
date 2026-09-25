// Apply a de.json translation table to Svelte components IN PLACE, via compiler AST offsets.
// Usage: node apply.mjs <src-dir> <de.json>
// de.json: { "<normalized English>": "<German>", "<file relative to src>::<normalized English>": "<German>", ... }
// Only visible text nodes and whitelisted display attributes are replaced. After patching,
// every file is re-parsed and its AST (minus text content) must equal the original, or we exit 1.
import { parse } from 'svelte/compiler';
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const ATTRS = new Set(['placeholder', 'title', 'aria-label', 'alt', 'label', 'aria-description']);
const [root, tablePath] = process.argv.slice(2);
const table = JSON.parse(readFileSync(tablePath, 'utf8'));

function* walkFiles(dir) {
	for (const name of readdirSync(dir)) {
		const p = join(dir, name);
		if (statSync(p).isDirectory()) yield* walkFiles(p);
		else if (p.endsWith('.svelte')) yield p;
	}
}

const norm = (s) => s.replace(/\s+/g, ' ').trim();

function targets(node, out = []) {
	if (!node || typeof node !== 'object') return out;
	if (Array.isArray(node)) {
		node.forEach((n) => targets(n, out));
		return out;
	}
	if (node.type === 'Attribute') {
		const v = node.value;
		if (ATTRS.has(node.name) && Array.isArray(v) && v.length === 1 && v[0].type === 'Text') out.push(v[0]);
		return out;
	}
	if (node.type === 'Text') {
		out.push(node);
		return out;
	}
	for (const [k, v] of Object.entries(node)) {
		if (k === 'instance' || k === 'module' || k === 'css' || k === 'expression' || k === 'metadata') continue;
		if (v && typeof v === 'object') targets(v, out);
	}
	return out;
}

// structural fingerprint: drop positions and text payloads, keep everything else
function shape(node) {
	if (Array.isArray(node)) return node.map(shape);
	if (!node || typeof node !== 'object') return node;
	const o = {};
	for (const [k, v] of Object.entries(node)) {
		if (['start', 'end', 'loc', 'range', 'metadata', 'raw', 'data', 'value_raw'].includes(k)) continue;
		if (node.type === 'Text' && k === 'value') continue;
		if (k === 'css') continue; // style content is untouched; offsets differ only
		o[k] = shape(v);
	}
	return o;
}

let files = 0, replaced = 0, untranslated = new Set(), used = new Set();
for (const f of walkFiles(root)) {
	const src = readFileSync(f, 'utf8');
	const ast = parse(src, { modern: true });
	const edits = [];
	for (const t of targets(ast.fragment)) {
		const raw = src.slice(t.start, t.end);
		const key = norm(raw);
		if (!/[A-Za-z]{2,}/.test(key)) continue;
		// a per-component override "<file relative to src>::<text>" wins over the plain key
		const scoped = `${relative(root, f)}::${key}`;
		const hit = scoped in table ? scoped : key in table ? key : undefined;
		if (hit === undefined) { untranslated.add(key); continue; }
		const de = table[hit];
		used.add(hit);
		const lead = raw.match(/^\s*/)[0], trail = raw.match(/\s*$/)[0];
		edits.push([t.start, t.end, lead + de + trail]);
	}
	if (!edits.length) continue;
	edits.sort((a, b) => b[0] - a[0]);
	let out = src;
	for (const [s, e, rep] of edits) out = out.slice(0, s) + rep + out.slice(e);
	const before = JSON.stringify(shape(ast.fragment));
	const after = JSON.stringify(shape(parse(out, { modern: true }).fragment));
	if (before !== after) {
		console.error(`STRUCTURE CHANGED: ${relative(root, f)} — aborting`);
		process.exit(1);
	}
	writeFileSync(f, out);
	files++;
	replaced += edits.length;
}
const stale = Object.keys(table).filter((k) => !used.has(k));
console.error(`patched files=${files} replacements=${replaced} untranslated-unique=${untranslated.size} stale-keys=${stale.length}`);
for (const k of stale) console.error(`  stale (not in source): ${k}`);
if (process.env.I18N_REPORT) writeFileSync(process.env.I18N_REPORT, JSON.stringify([...untranslated].sort(), null, 1));
