"""Build patch 0005: German plurals. Run inside a pristine upstream checkout's src/ directory."""
import re

HELPER = """// roamarr-de: German count + noun ("1 Reise", "3 Reisen"). Upstream builds English plurals
// with `word{n === 1 ? '' : 's'}`, which can't express German plural forms.
export function pl(n: number, one: string, other: string): string {
\treturn `${n} ${n === 1 ? one : other}`;
}
"""
open('lib/pluralDe.ts', 'w').write(HELPER)

SVELTE_IMPORT = "<script lang=\"ts\">\n\timport { pl } from '$lib/pluralDe';\n"
TS_IMPORT = "import { pl } from '$lib/pluralDe';\n"

S = "''"  # readability helper for the English suffix pattern below
def eng(expr, word):
    return f"{{{expr}}} {word}{{{expr} === 1 ? {S} : 's'}}"

edits = {
    'routes/+page.svelte': [
        (f'You have <a href="/notifications" class="link">{eng("data.stats.unread", "unread alert")}</a>.',
         'Du hast <a href="/notifications" class="link">{pl(data.stats.unread, \'ungelesene Benachrichtigung\', \'ungelesene Benachrichtigungen\')}</a>.'),
    ],
    'routes/search/+page.svelte': [
        (eng('data.trips.length', 'trip') + ' found', "{pl(data.trips.length, 'Reise', 'Reisen')} gefunden"),
    ],
    'routes/notifications/+page.svelte': [
        (eng('unread', 'unread alert'), "{pl(unread, 'ungelesene Benachrichtigung', 'ungelesene Benachrichtigungen')}"),
    ],
    'routes/groups/+page.svelte': [
        ("return `${count} member${count === 1 ? '' : 's'}`;", "return pl(count, 'Mitglied', 'Mitglieder');"),
    ],
    'routes/trips/+page.svelte': [
        (eng('data.trips.length', 'trip') + ' planned', "{pl(data.trips.length, 'Reise', 'Reisen')} geplant"),
    ],
    'routes/trips/import/+page.svelte': [
        (re.compile(r"\{form\.dryRun \? 'Would import' : 'Imported'\} \{form\.result\.imported\} trip\{form\.result\.imported === 1 \? '' : 's'\} with\s+\{form\.result\.segmentCount\} segment\{form\.result\.segmentCount === 1 \? '' : 's'\}\."),
         "{pl(form.result.imported, 'Reise', 'Reisen')} mit {pl(form.result.segmentCount, 'Reiseabschnitt', 'Reiseabschnitten')} {form.dryRun ? 'würden importiert' : 'importiert'}."),
        (eng('p.segments.length', 'segment'), "{pl(p.segments.length, 'Abschnitt', 'Abschnitte')}"),
    ],
    'routes/trips/[id]/+page.svelte': [
        ('Starts in ' + eng('daysUntil', 'day'), "Beginnt in {pl(daysUntil, 'Tag', 'Tagen')}"),
        (eng('days', 'day'), "{pl(days, 'Tag', 'Tage')}"),
        (eng('segmentList.length', 'segment'), "{pl(segmentList.length, 'Abschnitt', 'Abschnitte')}"),
        (eng('group.segments.length', 'segment'), "{pl(group.segments.length, 'Abschnitt', 'Abschnitte')}"),
        (eng('prepItemCount', 'item'), "{pl(prepItemCount, 'Eintrag', 'Einträge')}"),
    ],
    'routes/trips/[id]/print/+page.svelte': [
        (eng('days', 'day'), "{pl(days, 'Tag', 'Tage')}"),
        (eng('segmentList.length', 'segment'), "{pl(segmentList.length, 'Abschnitt', 'Abschnitte')}"),
    ],
    'routes/profile/email_processing/+page.server.ts': [
        ("`Inbox checked. ${result.imported} itinerary item${result.imported === 1 ? '' : 's'} imported.`",
         "`Posteingang geprüft. ${pl(result.imported, 'Reiseeintrag', 'Reiseeinträge')} importiert.`"),
    ],
    'routes/profile/security/+page.svelte': [
        (eng('tfa.backupCodesRemaining', 'backup code') + ' remaining.', "Noch {pl(tfa.backupCodesRemaining, 'Backup-Code', 'Backup-Codes')} übrig."),
    ],
    'routes/places/import/+page.svelte': [
        ('Preview — ' + eng('preview.length', 'row') + ' from {form?.sourceName}', "Vorschau — {pl(preview.length, 'Zeile', 'Zeilen')} aus {form?.sourceName}"),
        (re.compile(r"\{duplicateCount\} possible duplicate\{duplicateCount === 1 \? '' : 's'\} detected\s+\(exact name or within 50 m of an existing place\)\."),
         "{pl(duplicateCount, 'mögliches Duplikat', 'mögliche Duplikate')} erkannt (gleicher Name oder höchstens 50 m von einem vorhandenen Ort entfernt)."),
        ('Import ' + eng('selectedRows.length', 'place'), "{pl(selectedRows.length, 'Ort', 'Orte')} importieren"),
        ('Imported ' + eng('form.imported.created', 'place'), "{pl(form.imported.created, 'Ort', 'Orte')} importiert"),
        ('— skipped ' + eng('form.imported.skippedDuplicates', 'duplicate'), "— {pl(form.imported.skippedDuplicates, 'Duplikat', 'Duplikate')} übersprungen"),
    ],
    'routes/cards/+page.svelte': [
        ("return count === 0 ? 'No benefits' : `${count} benefit${count === 1 ? '' : 's'}`;",
         "return count === 0 ? 'Keine Leistungen' : pl(count, 'Leistung', 'Leistungen');"),
    ],
    'routes/profile/visited/shared.server.ts': [
        ("parts.push(`${added.countries.length} countr${added.countries.length === 1 ? 'y' : 'ies'}`);", "parts.push(pl(added.countries.length, 'Land', 'Länder'));"),
        ("parts.push(`${added.states.length} U.S. state${added.states.length === 1 ? '' : 's'}`);", "parts.push(pl(added.states.length, 'US-Bundesstaat', 'US-Bundesstaaten'));"),
        ("`Marked ${parts.join(' and ')} from past trips.` : 'No new places found from past trips.'",
         "`${parts.join(' und ')} aus vergangenen Reisen als besucht markiert.` : 'Keine neuen Orte aus vergangenen Reisen gefunden.'"),
    ],
    'lib/server/tripMetaActions.ts': [
        ("`Optimized ${result.orderedSegmentIds.length} stop${result.orderedSegmentIds.length === 1 ? '' : 's'} (${(result.totalDistanceMeters / 1000).toFixed(1)} km).`",
         "`${pl(result.orderedSegmentIds.length, 'Stopp', 'Stopps')} optimiert (${(result.totalDistanceMeters / 1000).toFixed(1)} km).`"),
        ("'Nothing to optimize for this day.'", "'Für diesen Tag gibt es nichts zu optimieren.'"),
        ("parts.push(`${added.countries.length} countr${added.countries.length === 1 ? 'y' : 'ies'}`);", "parts.push(pl(added.countries.length, 'Land', 'Länder'));"),
        ("parts.push(`${added.states.length} U.S. state${added.states.length === 1 ? '' : 's'}`);", "parts.push(pl(added.states.length, 'US-Bundesstaat', 'US-Bundesstaaten'));"),
        ("`Marked ${parts.join(' and ')} visited from this trip.`", "`${parts.join(' und ')} aus dieser Reise als besucht markiert.`"),
        ("'No new places to mark from this trip.'", "'Keine neuen Orte aus dieser Reise zu markieren.'"),
    ],
}

total = 0
for path, reps in edits.items():
    t = open(path, encoding='utf-8').read()
    for old, new in reps:
        if isinstance(old, re.Pattern):
            t, n = old.subn(lambda m: new, t)
        else:
            n = t.count(old)
            t = t.replace(old, new)
        assert n >= 1, f'{path}: no match for {getattr(old, "pattern", old)[:80]}'
        total += n
    if path.endswith('.svelte'):
        assert t.startswith('<script lang="ts">\n'), path
        t = t.replace('<script lang="ts">\n', SVELTE_IMPORT, 1)
    else:
        t = TS_IMPORT + t
    open(path, 'w', encoding='utf-8').write(t)
print(f'plural sites replaced: {total} in {len(edits)} files')
