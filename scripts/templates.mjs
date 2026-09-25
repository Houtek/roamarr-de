// Template-literal translation: `Delete category ${c.name}? …` → `Kategorie ${c.name} löschen? …`
//
//   node templates.mjs extract <src-dir>                 → JSON candidates on stdout
//   node templates.mjs apply   <src-dir> <de.templates.json>
//
// Key format: the literal's text with each ${expr} replaced by ${0}, ${1}, … in source order,
// whitespace-normalized. de.templates.json: { "<file>": { "<key>": "<German with ${n}>" } }.
// German must use every placeholder exactly once and may reorder them. Covers template literals in
// Svelte <script> blocks, in markup expressions ({`…`}, attr={`…`}) and in .ts modules.
// apply is atomic, re-parses each file and compares the AST with template text stripped and
// template expressions compared as a multiset (they may move).
import { parse } from 'svelte/compiler';
import { Parser } from 'acorn';
import { tsPlugin } from '@sveltejs/acorn-typescript';
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const TS = Parser.extend(tsPlugin());
const [mode, root, tablePath] = process.argv.slice(2);

function roots(file, src) {
	if (file.endsWith('.svelte')) {
		const ast = parse(src, { modern: true });
		return [ast.instance?.content, ast.module?.content, ast.fragment].filter(Boolean);
	}
	return [TS.parse(src, { sourceType: 'module', ecmaVersion: 'latest' })];
}

function templates(node, out = []) {
	if (!node || typeof node !== 'object') return out;
	if (Array.isArray(node)) {
		for (const n of node) templates(n, out);
		return out;
	}
	if (node.type === 'TemplateLiteral') out.push(node);
	for (const [k, v] of Object.entries(node)) {
		if (k === 'loc' || k === 'range' || k === 'metadata') continue;
		if (v && typeof v === 'object') templates(v, out);
	}
	return out;
}

const norm = (s) => s.replace(/\s+/g, ' ').trim();
function keyOf(src, t) {
	let k = '';
	t.quasis.forEach((q, i) => {
		k += q.value.raw;
		if (i < t.expressions.length) k += '${' + i + '}';
	});
	return norm(k);
}
// prose heuristic: at least two words of 2+ letters outside placeholders, and a space
const prose = (key) => /[A-Za-z]{2,}[^$]*\s+[A-Za-z]{2,}/.test(key.replace(/\$\{\d+\}/g, ' '));

function shape(node) {
	if (typeof node === 'bigint') return `${node}n`; // JSON.stringify can't serialize BigInt literals (e.g. 0n)
	if (Array.isArray(node)) return node.map(shape);
	if (!node || typeof node !== 'object') return node;
	const o = {};
	for (const [k, v] of Object.entries(node)) {
		if (['start', 'end', 'loc', 'range', 'metadata', 'raw', 'css'].includes(k)) continue;
		if (node.type === 'TemplateLiteral' && k === 'quasis') { o.quasis = v.length; continue; }
		if (node.type === 'TemplateLiteral' && k === 'expressions') { o.expressions = v.map((e) => JSON.stringify(shape(e))).sort(); continue; }
		if (node.type === 'Text' && (k === 'data' || k === 'value')) continue;
		o[k] = shape(v);
	}
	return o;
}

function* walk(dir) {
	for (const n of readdirSync(dir)) {
		const p = join(dir, n);
		if (statSync(p).isDirectory()) yield* walk(p);
		else if (/\.(svelte|ts)$/.test(p) && !/\.(test|spec)\.ts$/.test(p)) yield p;
	}
}

if (mode === 'extract') {
	const out = [];
	for (const f of walk(root)) {
		const file = relative(root, f);
		if (/(^|\/)(api|mcp)\/|\+server\.ts$|mcpServer\.ts$|mongrelMigrations/.test(file)) continue;
		const src = readFileSync(f, 'utf8');
		const seen = new Set();
		for (const r of roots(file, src)) {
			for (const t of templates(r)) {
				const key = keyOf(src, t);
				if (!prose(key) || seen.has(key)) continue;
				seen.add(key);
				const line = src.slice(0, t.start).split('\n').length;
				out.push({ file, line, key, exprs: t.expressions.map((e) => src.slice(e.start, e.end)) });
			}
		}
	}
	console.error(`template candidates=${out.length} files=${new Set(out.map((x) => x.file)).size}`);
	console.log(JSON.stringify(out, null, 1));
} else if (mode === 'apply') {
	const table = JSON.parse(readFileSync(tablePath, 'utf8'));
	const pending = [], problems = [];
	let replaced = 0;
	for (const [file, map] of Object.entries(table)) {
		const path = join(root, file);
		const src = readFileSync(path, 'utf8');
		const before = roots(file, src);
		const edits = [], hits = new Set();
		for (const r of before) {
			for (const t of templates(r)) {
				const key = keyOf(src, t);
				if (!(key in map)) continue;
				const de = map[key];
				const used = [...de.matchAll(/\$\{(\d+)\}/g)].map((m) => Number(m[1])).sort((a, b) => a - b);
				if (used.join() !== t.expressions.map((_, i) => i).join()) {
					problems.push(`${file}: placeholders in German don't match: ${key}`);
					continue;
				}
				const esc = (s) => s.replace(/\\/g, '\\\\').replace(/`/g, '\\`');
				const parts = de.split(/(\$\{\d+\})/);
				const body = parts
					.map((p) => {
						const m = p.match(/^\$\{(\d+)\}$/);
						return m ? '${' + src.slice(t.expressions[m[1]].start, t.expressions[m[1]].end) + '}' : esc(p).replace(/\$\{/g, '\\${');
					})
					.join('');
				edits.push([t.start, t.end, '`' + body + '`']);
				hits.add(key);
			}
		}
		for (const k of Object.keys(map)) if (!hits.has(k)) problems.push(`${file}: unmatched: ${k}`);
		if (!edits.length) continue;
		edits.sort((a, b) => b[0] - a[0]);
		let out = src;
		for (const [s, e, rep] of edits) out = out.slice(0, s) + rep + out.slice(e);
		if (JSON.stringify(before.map(shape)) !== JSON.stringify(roots(file, out).map(shape))) {
			problems.push(`${file}: STRUCTURE CHANGED`);
			continue;
		}
		pending.push([path, out]);
		replaced += edits.length;
	}
	console.error(`templates: patched files=${pending.length} replacements=${replaced} problems=${problems.length}`);
	if (problems.length) {
		for (const p of problems) console.error(`  ${p}`);
		console.error('nothing written');
		process.exit(1);
	}
	for (const [path, out] of pending) writeFileSync(path, out);
} else {
	console.error('usage: templates.mjs extract <src> | apply <src> <de.templates.json>');
	process.exit(2);
}
