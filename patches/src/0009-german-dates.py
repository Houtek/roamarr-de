"""Build patch 0009: German dates. Run inside src/ with 0001-0008 applied.

- Luxon takes month/weekday names from each DateTime's locale (server default en-US, client = browser).
  A tiny module sets Settings.defaultLocale = 'de'; it is imported by dateFormat.ts, the root layout and
  hooks.server.ts so it is active on server and client before anything formats. Nothing in the code parses
  dates with Luxon (no fromFormat), and all textual formats are UI display, so this is display-only.
- dateFormat.ts: Intl 'en-US' → 'de-DE'; sample labels become the real German rendering; adds the usual
  German formats (dd.MM.yyyy, d. MMMM yyyy) as selectable options (the settings validation uses this list).
- Trip page: US-ordered patterns ('LLL d, yyyy', 'h:mm a') → German order and 24-hour time.
"""
open('lib/luxonDe.ts', 'w', encoding='utf-8').write(
    "// roamarr-de: German month/weekday names for every Luxon DateTime (server and client).\n"
    "import { Settings } from 'luxon';\n\n"
    "Settings.defaultLocale = 'de';\n"
)

def edit(path, reps, prepend=None, after_script=None):
    t = open(path, encoding='utf-8').read()
    for a, b in reps:
        assert t.count(a) >= 1, (path, a[:70])
        t = t.replace(a, b)
    if prepend:
        t = prepend + t
    if after_script:
        assert t.startswith('<script lang="ts">\n'), path
        t = t.replace('<script lang="ts">\n', '<script lang="ts">\n' + after_script, 1)
    open(path, 'w', encoding='utf-8').write(t)

edit('hooks.server.ts', [], prepend="import '$lib/luxonDe';\n")
edit('routes/+layout.svelte', [], after_script="\timport '$lib/luxonDe';\n")

edit('lib/dateFormat.ts', [
    ("import { DateTime } from 'luxon';\n", "import { DateTime } from 'luxon';\nimport './luxonDe';\n"),
    ("new Intl.DateTimeFormat('en-US', {", "new Intl.DateTimeFormat('de-DE', {"),  # both occurrences
    ("\t{ value: 'MMM d, yyyy', label: 'Jul 29, 2026' },\n\t{ value: 'd MMM yyyy', label: '29 Jul 2026' },\n\t{ value: 'EEEE, MMM d, yyyy', label: 'Tuesday, July 29, 2026' }\n];",
     "\t{ value: 'MMM d, yyyy', label: 'Juli 29, 2026' },\n\t{ value: 'd MMM yyyy', label: '29 Juli 2026' },\n\t{ value: 'EEEE, MMM d, yyyy', label: 'Mittwoch, Juli 29, 2026' },\n"
     "\t// roamarr-de: the usual German formats\n\t{ value: 'dd.MM.yyyy', label: '29.07.2026' },\n\t{ value: 'd. MMMM yyyy', label: '29. Juli 2026' },\n\t{ value: 'EEEE, d. MMMM yyyy', label: 'Mittwoch, 29. Juli 2026' }\n];"),
    ("\t{ value: 'MMM d, yyyy h:mm a', label: 'Jul 29, 2026 12:34 PM' },\n\t{ value: 'MMM d, yyyy HH:mm', label: 'Jul 29, 2026 12:34' },\n\t{ value: 'd MMM yyyy HH:mm', label: '29 Jul 2026 12:34' },\n\t{ value: 'd MMM yyyy HH:mm:ss', label: '29 Jul 2026 12:34:56' }\n];",
     "\t{ value: 'MMM d, yyyy h:mm a', label: 'Juli 29, 2026 12:34 PM' },\n\t{ value: 'MMM d, yyyy HH:mm', label: 'Juli 29, 2026 12:34' },\n\t{ value: 'd MMM yyyy HH:mm', label: '29 Juli 2026 12:34' },\n\t{ value: 'd MMM yyyy HH:mm:ss', label: '29 Juli 2026 12:34:56' },\n"
     "\t// roamarr-de: the usual German formats\n\t{ value: 'dd.MM.yyyy HH:mm', label: '29.07.2026 12:34' },\n\t{ value: 'd. MMMM yyyy, HH:mm', label: '29. Juli 2026, 12:34' }\n];"),
])

edit('routes/trips/[id]/+page.svelte', [
    ("toFormat('LLLL d, yyyy')", "toFormat('d. MMMM yyyy')"),
    ("toFormat('LLL d, yyyy')", "toFormat('d. MMM yyyy')"),
    ("toFormat('LLL d')", "toFormat('d. MMM')"),
    ("toFormat('EEE, MMM d')", "toFormat('EEE, d. MMM')"),
    ("toFormat('h:mm a')", "toFormat('HH:mm')"),
])
print('german dates: luxon locale, Intl de-DE, format options, trip-page patterns')
