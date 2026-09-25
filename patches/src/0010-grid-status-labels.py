"""Build patch 0010: status labels inside HTML string literals in grid cell formatters.

`html('<span …>Active</span>')` puts English text inside an HTML string passed to a function, a position none
of the tables cover. Each label is display-only (only rendered in a grid cell; the logic branches on the raw
value before it, e.g. `status === 'sent'`). Run inside src/ with 0001-0009 applied.
"""
edits = {
    'routes/users/+page.svelte': [
        ('var(--theme-readable)">Admin</span>', 'var(--theme-readable)">Admin</span>'),  # unchanged on purpose: "Admin" is German UI usage too
        ('var(--theme-readable-muted)">User</span>', 'var(--theme-readable-muted)">Benutzer</span>'),
        ('#b91c1c)">Disabled</span>', '#b91c1c)">Deaktiviert</span>'),
        ('var(--theme-readable)">Active</span>', 'var(--theme-readable)">Aktiv</span>'),
        ('#b45309)">Password reset required</span>', '#b45309)">Passwortänderung erforderlich</span>'),
        ('var(--theme-readable)">2FA enabled</span>', 'var(--theme-readable)">2FA aktiviert</span>'),
    ],
    'routes/fare-providers/+page.svelte': [
        ('var(--theme-readable)">Enabled</span>', 'var(--theme-readable)">Aktiviert</span>'),
        ('var(--theme-readable-faint)">Disabled</span>', 'var(--theme-readable-faint)">Deaktiviert</span>'),
    ],
    'routes/job-history/+page.svelte': [
        ('#b91c1c)">Failed</span>', '#b91c1c)">Fehlgeschlagen</span>'),
        ('#b45309)">Running</span>', '#b45309)">Läuft</span>'),
    ],
    'routes/profile/documents/+page.svelte': [
        ('var(--theme-readable-faint)">Me</span>', 'var(--theme-readable-faint)">Ich</span>'),
    ],
    'routes/profile/loyalty/+page.svelte': [
        ('var(--theme-readable-faint)">Never</span>', 'var(--theme-readable-faint)">Nie</span>'),
    ],
    'routes/profile/reminders/+page.svelte': [
        ('var(--theme-readable)">Sent</span>', 'var(--theme-readable)">Gesendet</span>'),
        ('#b45309)">Sending</span>', '#b45309)">Wird gesendet</span>'),
        ('var(--theme-readable-muted)">Pending</span>', 'var(--theme-readable-muted)">Ausstehend</span>'),
    ],
}
n = 0
for path, reps in edits.items():
    t = open(path, encoding='utf-8').read()
    for a, b in reps:
        assert t.count(a) == 1, (path, a, t.count(a))
        t = t.replace(a, b)
        n += a != b
    open(path, 'w', encoding='utf-8').write(t)
print(f'grid status labels: {n} translated')
