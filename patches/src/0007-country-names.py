"""Build patch 0007: German country names via Intl.DisplayNames. Run inside src/ with 0001-0006 applied."""
p = 'lib/countries.ts'
t = open(p, encoding='utf-8').read()
assert t.startswith('export const COUNTRIES = [\n'), 'unexpected countries.ts head'
assert t.rstrip().endswith('] as const;'), 'unexpected countries.ts tail'
t = t.replace('export const COUNTRIES = [\n', 'const COUNTRIES_EN = [\n', 1)
t = t.rstrip() + """

// roamarr-de: German country names derived from the ISO code (Intl.DisplayNames, available in Node and
// all browsers), sorted German-alphabetically. Lookups everywhere go by `code`; `name` is display + search.
const DE_REGION_NAMES = new Intl.DisplayNames(['de'], { type: 'region' });
export const COUNTRIES = COUNTRIES_EN.map((c) => ({ code: c.code, name: DE_REGION_NAMES.of(c.code) ?? c.name })).sort(
\t(a, b) => a.name.localeCompare(b.name, 'de')
);
"""
open(p, 'w', encoding='utf-8').write(t)
print('countries: German names via Intl.DisplayNames')
