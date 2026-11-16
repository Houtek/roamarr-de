"""Build patch 0012: stored enum keys rendered raw with CSS `capitalize` → German display names.

Upstream prints keys such as `lodging`, `adult`, `private`, `not_going` directly and relies on CSS
`text-transform: capitalize`. Keys stay the stored values; only the render sites look up a German name
(falling back to the old underscore-to-space display for unknown keys). Run inside src/ with the lower-numbered patches applied.
"""
open('lib/enumDe.ts', 'w', encoding='utf-8').write("""// roamarr-de: German display names for stored enum keys (keys themselves stay unchanged).
const MAPS = {
\tvisibility: { private: 'Privat', groups: 'Gruppen', public: 'Öffentlich' },
\tdocumentType: { passport: 'Reisepass', drivers_license: 'Führerschein', global_entry: 'Global Entry', visa: 'Visum', national_id: 'Personalausweis' },
\tcompanion: { adult: 'Erwachsener', child: 'Kind', other: 'Sonstige', guide: 'Reiseführer', driver: 'Fahrer' },
\texpense: { lodging: 'Unterkunft', transport: 'Transport', food: 'Essen', activities: 'Aktivitäten', other: 'Sonstiges' },
\tattendee: { going: 'Dabei', maybe: 'Vielleicht', not_going: 'Nicht dabei' },
\treminder: { pending: 'Ausstehend', sending: 'Wird gesendet', sent: 'Gesendet' },
\tmailHold: { requested: 'Beantragt', active: 'Aktiv', ended: 'Beendet', cancelled: 'Storniert' }
} as const satisfies Record<string, Record<string, string>>;

export function deEnum(kind: keyof typeof MAPS, value: unknown): string {
\tconst key = String(value ?? '');
\treturn (MAPS[kind] as Record<string, string>)[key] ?? key.replaceAll('_', ' ');
}
""")

IMPORT = "\timport { deEnum } from '$lib/enumDe';\n"
edits = {
    'lib/components/TripCard.svelte': [
        ("{trip.defaultVisibility || 'private'}", "{deEnum('visibility', trip.defaultVisibility || 'private')}"),
    ],
    'routes/+page.svelte': [
        ("{d.type.replace('_', ' ')}", "{deEnum('documentType', d.type)}"),
    ],
    'routes/trips/[id]/+page.svelte': [
        ("{ownerTrip.defaultVisibility}", "{deEnum('visibility', ownerTrip.defaultVisibility)}"),
        ("{a.status.replace('_', ' ')}", "{deEnum('attendee', a.status)}"),
        ("capitalize\">{r.status}", "capitalize\">{deEnum('reminder', r.status)}"),
        ("{budget.category}</strong>", "{deEnum('expense', budget.category)}</strong>"),
        ("{e.category} · ", "{deEnum('expense', e.category)} · "),
        ("capitalize\">{c.category}</span>", "capitalize\">{deEnum('companion', c.category)}</span>"),
    ],
    # upstream >= 0.44: mail hold status in the badge and in both status <select>s (add + edit form)
    'lib/components/MailHoldsPanel.svelte': [
        ("{statusClass(hold.status)}\">{hold.status}</span>", "{statusClass(hold.status)}\">{deEnum('mailHold', hold.status)}</span>"),
        ("<option value={status}>{status}</option>", "<option value={status}>{deEnum('mailHold', status)}</option>", 2),
        # not an enum, but a confirm() call argument, which none of the table modes can reach
        ("confirm('Delete this mail hold?')", "confirm('Diese Postlagerung löschen?')"),
    ],
    'routes/trips/[id]/print/+page.svelte': [
        ("({c.category}", "({deEnum('companion', c.category)}"),
    ],
}
n = 0
for path, reps in edits.items():
    t = open(path, encoding='utf-8').read()
    for a, b, *cnt in reps:
        want = cnt[0] if cnt else 1
        assert t.count(a) == want, (path, a, t.count(a))
        t = t.replace(a, b)
        n += want
    assert t.startswith('<script lang="ts">\n'), path
    t = t.replace('<script lang="ts">\n', '<script lang="ts">\n' + IMPORT, 1)
    open(path, 'w', encoding='utf-8').write(t)
print(f'enum labels: {n} render sites')
