// Translate reviewed string literals in SCRIPT code (Svelte <script> blocks and .ts modules), in place.
// Usage: node apply-script.mjs <src-dir> <de.script.json> [property|expr]
// de.script.json: { "<file relative to src>": { "<English literal>": "<German>", ... }, ... }
// Only string literals that are the VALUE of an object property are touched (`label: 'Trips'`,
// `fail(400, { error: '...' })`). Every entry was reviewed as display-only for that file.
// Mode `expr` (table de.expr.json) instead matches literals in value positions that aren't properties:
// conditional branches (a ? 'X' : 'Y'), fallbacks (x ?? 'X', x || 'X'), `return 'X'` and markup {'X'},
// in <script> AND in Svelte markup expressions. Separate table, so each mode's entries keep their meaning.
// After patching, the file is re-parsed and its AST (minus literal values and positions) must be
// unchanged, every entry must have matched at least once, or we exit 1.
import { parse } from 'svelte/compiler';
import { Parser } from 'acorn';
import { tsPlugin } from '@sveltejs/acorn-typescript';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const [root, tablePath, mode = 'property'] = process.argv.slice(2);
if (!['property', 'expr'].includes(mode)) throw new Error(`unknown mode ${mode}`);
const table = JSON.parse(readFileSync(tablePath, 'utf8'));
const TS = Parser.extend(tsPlugin());

function programs(file, src) {
	if (file.endsWith('.svelte')) {
		const ast = parse(src, { modern: true });
		return { progs: [ast.instance?.content, ast.module?.content].filter(Boolean), markup: ast.fragment };
	}
	return { progs: [TS.parse(src, { sourceType: 'module', ecmaVersion: 'latest' })], markup: null };
}

function matches(node, parent) {
	if (mode === 'property') return parent.type === 'Property' && parent.value === node;
	return (
		(parent.type === 'ConditionalExpression' && (parent.consequent === node || parent.alternate === node)) ||
		(parent.type === 'LogicalExpression' && parent.right === node && ['??', '||'].includes(parent.operator)) ||
		parent.type === 'ReturnStatement' ||
		parent.type === 'ExpressionTag'
	);
}

function propertyStringLiterals(node, out = [], parent = null) {
	if (!node || typeof node !== 'object') return out;
	if (Array.isArray(node)) {
		for (const n of node) propertyStringLiterals(n, out, parent);
		return out;
	}
	if (node.type === 'Literal' && typeof node.value === 'string' && parent && matches(node, parent)) {
		out.push(node);
	}
	for (const [k, v] of Object.entries(node)) {
		if (k === 'loc' || k === 'range' || k === 'metadata') continue;
		if (v && typeof v === 'object') propertyStringLiterals(v, out, node);
	}
	return out;
}

function shape(node) {
	if (Array.isArray(node)) return node.map(shape);
	if (!node || typeof node !== 'object') return node;
	const o = {};
	for (const [k, v] of Object.entries(node)) {
		if (['start', 'end', 'loc', 'range', 'metadata', 'raw'].includes(k)) continue;
		if (node.type === 'Literal' && k === 'value') continue;
		if (k === 'css') continue;
		o[k] = shape(v);
	}
	return o;
}

const quote = (q, s) => q + s.replace(/\\/g, '\\\\').replace(new RegExp(q, 'g'), '\\' + q) + q;

let files = 0, replaced = 0;
const unmatched = [];
const pending = []; // written only if every file and entry checks out
for (const [file, map] of Object.entries(table)) {
	const path = join(root, file);
	const src = readFileSync(path, 'utf8');
	const before = programs(file, src);
	const edits = [];
	const hits = new Set();
	for (const prog of mode === 'expr' && before.markup ? [...before.progs, before.markup] : before.progs) {
		for (const lit of propertyStringLiterals(prog)) {
			if (!(lit.value in map)) continue;
			const q = src[lit.start];
			if (q !== "'" && q !== '"') continue; // template literals are never touched
			edits.push([lit.start, lit.end, quote(q, map[lit.value])]);
			hits.add(lit.value);
		}
	}
	for (const en of Object.keys(map)) if (!hits.has(en)) unmatched.push(`${file}: ${en}`);
	if (!edits.length) continue;
	edits.sort((a, b) => b[0] - a[0]);
	let out = src;
	for (const [s, e, rep] of edits) out = out.slice(0, s) + rep + out.slice(e);
	const after = programs(file, out);
	const same =
		JSON.stringify(before.progs.map(shape)) === JSON.stringify(after.progs.map(shape)) &&
		JSON.stringify(shape(before.markup)) === JSON.stringify(shape(after.markup));
	if (!same) {
		console.error(`STRUCTURE CHANGED: ${file} — aborting`);
		process.exit(1);
	}
	pending.push([path, out]);
	files++;
	replaced += edits.length;
}
console.error(`script(${mode}): patched files=${files} replacements=${replaced} unmatched-entries=${unmatched.length}`);
if (unmatched.length) {
	for (const u of unmatched) console.error(`  unmatched (not a property-value literal in source): ${u}`);
	console.error('nothing written');
	process.exit(1);
}
for (const [path, out] of pending) writeFileSync(path, out);
