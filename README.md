# roamarr-de

A German UI for [Roamarr](https://github.com/visorcraft/Roamarr), applied at build time. This is a personal, unofficial translation kit and not a fork: upstream source is untouched in git. The translation is applied to a pinned upstream commit right before `npm run build`.

## How it works

- `scripts/extract.mjs` parses every `.svelte` component with the Svelte compiler and collects visible text nodes plus display attributes (`placeholder`, `title`, `aria-label`, `alt`, `label`, `aria-description`). The result is `strings.en.json`.
- `de.json` maps the whitespace-normalized English string to German. A key of the form `<file relative to src>::<text>` overrides the plain key for that one component, for short fragments whose German depends on context (e.g. `on` is `am` before a date but `für` before a path).
- `scripts/merge-chunks.mjs` validates translator output before it lands in `de.json`. It hard-fails on markup characters, entity drift, surrounding whitespace or key/order mismatches, and warns on formal address and colon drift.
- `expected-test-failures.txt` lists upstream tests that assert English wording; `compare-tests.mjs` tolerates exactly those and nothing else.
- `scripts/apply.mjs` replaces those strings in place, using the compiler's exact source offsets, so code, CSS classes and expressions cannot be touched. It then re-parses every patched file and exits 1 if the syntax tree differs from the original in anything but text. A translation containing `{`, `<` or similar markup therefore fails the build instead of changing behaviour.
- Strings missing from `de.json` stay English. After an upstream bump, changed strings fall back to English and are listed in `untranslated.json`, and keys no longer found in the source are reported as stale.

## Code patches

Some text can't be translated by the table because it lives in script code or is also used as data. These get small, explicit patches in `patches/`, applied with `git apply` to the **pristine** upstream tree before the table runs. If upstream moves the patched lines, `git apply` fails and the build stops, instead of patching the wrong place.

- `0001-nav-labels.patch`: the sidebar and profile tabs. Navigation labels are also the data keys (expand state, `{#each}` keys, `section.label === 'Plan'`), so the data stays English and only the five render sites look up a German display name in `src/lib/navDe.ts`. `scripts/check-nav.mjs` fails the build if upstream adds a label without a German name.
- `0002-scope-descriptions.patch`: German descriptions for the 69 OAuth/API-key scopes in `src/lib/oauthScopes.ts` (API keys page, security page, OAuth consent). Scope names like `segments:read` stay English; only the descriptions are display text.

- `0004-grid-pagination.patch`: table footer ("Zeilen", "Zeige 1-10 von 23", page-button tooltips). `GridTable` parses grid.js's own English summary with a regex, so grid.js's language config deliberately stays English and only the rebuilt output is German.
- `0006-currency-defaults.patch`: **behaviour fix, not translation.** Upstream prefills currency inputs (add expense, new insurance, card benefit, trip base-currency fallback) with a hardcoded `USD`, ignoring the user's default currency. The patch prefills the profile's default currency instead (fallback USD).
- `0003-derived-labels.patch`: expense categories and payment statuses on the trip page, whose labels upstream computes by capitalizing the stored key (`lodging` → "Lodging"). The keys stay; a German map is consulted first.

## Script strings (`de.script.json`)

String literals in script code (`label: 'Notes'`, `fail(400, { error: '…' })`, default place categories) are translated by `scripts/apply-script.mjs`. Every entry was reviewed per file as **display-only**: shown to a human, and never compared, used as a key, persisted as identity or returned to a programmatic client. Kept English on purpose: MCP tool descriptions and errors (for AI clients), JSON API errors, brand names (map providers, themed theme names), and seed data inside database migrations. The applier only touches literals that are property values, re-parses each file and refuses to write anything if the structure changed or if any entry didn't match.

## Usage

```bash
npm ci
node scripts/extract.mjs <roamarr>/src > strings.en.json   # on a pristine tree
I18N_REPORT=untranslated.json scripts/build-de.sh <roamarr>  # patches, nav check, table
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
