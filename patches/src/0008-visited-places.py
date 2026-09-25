"""Build patch 0008: the shared visited countries / U.S. states page. Run inside src/ with 0001-0007 applied.

The component inserts English nouns ("countries", "U.S. state") into sentences at runtime. German needs
gender/case-specific forms, so the nouns become German and the sentences around them are rewritten whole.
The three template literals using ${noun}/${plural} are already covered by de.templates.json.
"""
p = 'routes/profile/visited/VisitedPlacePage.svelte'
t = open(p, encoding='utf-8').read()
reps = [
    ("const title = $derived(isCountry ? 'Visited countries' : 'Visited U.S. states');",
     "const title = $derived(isCountry ? 'Besuchte Länder' : 'Besuchte US-Bundesstaaten');"),
    ("const noun = $derived(isCountry ? 'country' : 'U.S. state');",
     "const noun = $derived(isCountry ? 'Land' : 'US-Bundesstaat');"),
    ("const plural = $derived(isCountry ? 'countries' : 'U.S. states');",
     "const plural = $derived(isCountry ? 'Länder' : 'US-Bundesstaaten');"),
    ("const listLabel = $derived(isCountry ? 'Country List' : 'State List');",
     "const listLabel = $derived(isCountry ? 'Länderliste' : 'Liste der Bundesstaaten');"),
    ("Auto-mark: {data.autoMarkVisited ? 'ON' : 'OFF'}",
     "Automatisch markieren: {data.autoMarkVisited ? 'AN' : 'AUS'}"),
    ("{data.countryCount} of {COUNTRIES.length} countries &middot; {data.stateCount} of {US_STATES.length} U.S. states",
     "{data.countryCount} von {COUNTRIES.length} Ländern &middot; {data.stateCount} von {US_STATES.length} US-Bundesstaaten"),
    ('<option value="" disabled selected>Choose {noun}...</option>',
     '<option value="" disabled selected>{noun} auswählen …</option>'),
    ('<p class="meta">Toggle {plural} you have visited.</p>',
     '<p class="meta">Markiere die {plural}, die du besucht hast.</p>'),
]
for a, b in reps:
    assert t.count(a) == 1, (a[:70], t.count(a))
    t = t.replace(a, b)
open(p, 'w', encoding='utf-8').write(t)
print('visited page: nouns + 5 sentences')
