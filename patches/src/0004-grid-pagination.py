"""Build patch 0004: GridTable footer ("Zeilen", "Zeige 1-10 von 23", page-button tooltips).

GridTable reformats grid.js's English summary ("Showing 1 - 10 of 23") by regex and replaces it. grid.js
re-renders the summary later and appends its English text again; upstream's regex then matches the combined
text (it starts with "Showing") and cleans up. Our German output starts with "Zeige", so the regex must accept
both forms, or the cleanup loop breaks and both versions stay visible. grid.js's own language stays English.
Run inside src/ with 0001-0003 applied.
"""
p = 'lib/components/GridTable.svelte'
t = open(p, encoding='utf-8').read()
reps = [
    ("label.textContent = 'Rows';", "label.textContent = 'Zeilen';"),
    ("prev?.setAttribute('aria-label', 'Previous page');", "prev?.setAttribute('aria-label', 'Vorherige Seite');"),
    ("prev?.setAttribute('title', 'Previous page');", "prev?.setAttribute('title', 'Vorherige Seite');"),
    ("next?.setAttribute('aria-label', 'Next page');", "next?.setAttribute('aria-label', 'Nächste Seite');"),
    ("next?.setAttribute('title', 'Next page');", "next?.setAttribute('title', 'Nächste Seite');"),
    ("\t\tconst match = text.match(/^Showing\\s+(\\d+)(?:\\s+to\\s+|\\s*-\\s*)(\\d+)\\s+of\\s+(\\d+)/i);",
     "\t\t// roamarr-de: accept grid.js's English summary AND our own German output. grid.js re-renders and appends\n"
     "\t\t// its English text again; matching our German prefix lets this cleanup run again (as upstream's does).\n"
     "\t\tconst match = text.match(/^(?:Showing|Zeige)\\s+(\\d+)(?:\\s+to\\s+|\\s*-\\s*)(\\d+)\\s+(?:of|von)\\s+(\\d+)/i);"),
    ("document.createTextNode('Showing '),", "document.createTextNode('Zeige '),"),
    ("document.createTextNode(' of '),", "document.createTextNode(' von '),"),
]
for a, b in reps:
    assert t.count(a) == 1, (a[:70], t.count(a))
    t = t.replace(a, b)
open(p, 'w', encoding='utf-8').write(t)
print('grid footer: German output + bilingual cleanup regex')
