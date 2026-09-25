# roamarr-de

A German UI for [Roamarr](https://github.com/visorcraft/Roamarr), applied at build time. This is a personal, unofficial translation kit and not a fork: upstream source is untouched in git. The translation is applied to a pinned upstream commit right before `npm run build`.

## How it works

- `scripts/extract.mjs` parses every `.svelte` component with the Svelte compiler and collects visible text nodes plus display attributes (`placeholder`, `title`, `aria-label`, `alt`, `label`, `aria-description`). The result is `strings.en.json`.
- `de.json` maps the whitespace-normalized English string to German. A key of the form `<file relative to src>::<text>` overrides the plain key for that one component, for short fragments whose German depends on context (e.g. `on` is `am` before a date but `für` before a path).
- `scripts/merge-chunks.mjs` validates translator output before it lands in `de.json`. It hard-fails on markup characters, entity drift, surrounding whitespace or key/order mismatches, and warns on formal address and colon drift.
- `expected-test-failures.txt` lists upstream tests that assert English wording; `compare-tests.mjs` tolerates exactly those and nothing else.
- `scripts/apply.mjs` replaces those strings in place, using the compiler's exact source offsets, so code, CSS classes and expressions cannot be touched. It then re-parses every patched file and exits 1 if the syntax tree differs from the original in anything but text. A translation containing `{`, `<` or similar markup therefore fails the build instead of changing behaviour.
- Strings missing from `de.json` stay English. After an upstream bump, changed strings fall back to English and are listed in `untranslated.json`, and keys no longer found in the source are reported as stale.

## Usage

```bash
npm ci
node scripts/extract.mjs <roamarr>/src > strings.en.json
I18N_REPORT=untranslated.json node scripts/apply.mjs <roamarr>/src de.json
```

`UPSTREAM_REF` holds the upstream commit the table is maintained against.

## CI

Every push runs the upstream test suite twice, unpatched (baseline) and patched, plus build and `svelte-check` on the patched tree. `scripts/compare-tests.mjs` fails the run only for tests that fail *after* patching but not before, so pre-existing or environment-dependent failures don't mask real regressions.

## Translation style

- Informal "du", modern German software style. Buttons use the infinitive ("Speichern").
- Glossary: Trip = Reise, Segment = Reiseabschnitt (short: Abschnitt), Stay = Unterkunft, Share = Freigabe/teilen, Notes = Notizen, Scopes (OAuth) = Berechtigungen.
- HTML entities (`&nbsp;`, `&middot;` ...) and product names stay as they are.

## Known limits

- **Plurals built in code**, e.g. `{n} segment{n === 1 ? '' : 's'}` (22 occurrences in 11 files). The English suffix sits in an expression, so a table entry alone yields wrong German ("Abschnitts"). These need small targeted source patches; their fragments (`segment`, `day`, `trip`, `item`, `row`, `place`, `duplicate`, `possible duplicate`, `unread alert`) stay English until then.
- **Sentences split around values or tags** are translated per fragment. Where German word order needs the parts in a different order, the fragment translation is a compromise.
- **Strings in script code** (navigation labels, server-side error messages, roughly 270) are not covered yet.
- Dates and numbers follow the browser locale where upstream uses `toLocaleString`/`Intl`. The date format is an admin setting.

## License

GPL-3.0-only, same as Roamarr.
