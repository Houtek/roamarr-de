// Extract translatable UI strings from Svelte components via the compiler AST.
// Usage: node extract.mjs <src-dir> > strings.json
import { parse } from 'svelte/compiler';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const ATTRS = new Set(['placeholder', 'title', 'aria-label', 'alt', 'label', 'aria-description',
	// display-only component props (verified: never compared, keyed or transformed in the receiving components)
	'message', 'emptyMessage', 'addLabel', 'confirmLabel', 'hint', 'copiedLabel', 'actionLabel']);
const isTextAttr = (name) => ATTRS.has(name) || /^[a-z]+(Label|Placeholder)$/.test(name);
const root = process.argv[2];

function* walkFiles(dir) {
	for (const name of readdirSync(dir)) {
		const p = join(dir, name);
		if (statSync(p).isDirectory()) yield* walkFiles(p);
		else if (p.endsWith('.svelte')) yield p;
	}
}

const norm = (s) => s.replace(/\s+/g, ' ').trim();
const hasWords = (s) => /[A-Za-z]{2,}/.test(s);

const strings = new Map(); // key -> { kind, count, files:Set }

function add(key, kind, file) {
	if (!hasWords(key)) return;
	const e = strings.get(key) ?? { kind, count: 0, files: new Set() };
	e.count++;
	e.files.add(file);
	strings.set(key, e);
}

function visit(node, file) {
	if (!node || typeof node !== 'object') return;
	if (Array.isArray(node)) return node.forEach((n) => visit(n, file));
	if (node.type === 'Attribute') {
		const v = node.value;
		if (isTextAttr(node.name) && Array.isArray(v) && v.length === 1 && v[0].type === 'Text') {
			add(norm(v[0].raw ?? v[0].data), `attr:${node.name}`, file);
		}
		return; // never collect other attribute values
	}
	if (node.type === 'Text') {
		add(norm(node.raw ?? node.data), 'text', file);
		return;
	}
	for (const [k, v] of Object.entries(node)) {
		if (k === 'instance' || k === 'module' || k === 'css' || k === 'expression' || k === 'metadata') continue;
		if (v && typeof v === 'object') visit(v, file);
	}
}

let files = 0;
for (const f of walkFiles(root)) {
	const ast = parse(readFileSync(f, 'utf8'), { modern: true });
	visit(ast.fragment, relative(root, f));
	files++;
}

const out = [...strings].map(([en, e]) => ({ en, kind: e.kind, count: e.count, files: [...e.files].slice(0, 3) }));
out.sort((a, b) => b.count - a.count || a.en.localeCompare(b.en));
console.error(`files=${files} unique=${out.length} occurrences=${out.reduce((s, x) => s + x.count, 0)}`);
console.log(JSON.stringify(out, null, 1));
