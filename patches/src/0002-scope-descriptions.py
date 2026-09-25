import re, sys
DE = {
    'trips:read': 'Reisen und Reiseverlauf ansehen',
    'trips:write': 'Reisen anlegen, bearbeiten, löschen und archivieren',
    'segments:read': 'Reiseabschnitte ansehen (Flüge, Hotels, Termine)',
    'segments:write': 'Reiseabschnitte anlegen, bearbeiten, löschen und verschieben',
    'packing:read': 'Packlisten und Vorlagen ansehen',
    'packing:write': 'Packlisten und Vorlagenpunkte verwalten',
    'budgets:read': 'Reisebudgets und Ausgaben ansehen',
    'budgets:write': 'Budgetkategorien einer Reise festlegen oder ändern',
    'expenses:read': 'Reiseausgaben und Belege ansehen',
    'expenses:write': 'Reiseausgaben anlegen, bearbeiten und löschen',
    'places:read': 'Besuchte Länder und US-Bundesstaaten ansehen',
    'places:write': 'Länder und US-Bundesstaaten als besucht markieren oder die Markierung entfernen',
    'saved-places:read': 'Deine gespeicherten Orte und Kategorien ansehen',
    'saved-places:write': 'Gespeicherte Orte und Kategorien anlegen, bearbeiten und löschen',
    'day-notes:read': 'Tagesnotizen zu Reisen ansehen',
    'day-notes:write': 'Tagesnotizen zu Reisen anlegen, bearbeiten und löschen',
    'reminders:read': 'Deine Erinnerungen ansehen',
    'reminders:write': 'Deine Erinnerungen anlegen, bearbeiten und löschen',
    'profile:read': 'Reisedokumente und vorbereitete Zusammenfassungen lesen',
    'companions:read': 'Mitreisende ansehen',
    'companions:write': 'Mitreisende hinzufügen, bearbeiten oder entfernen',
    'sharing:read': 'Reisefreigaben und Gruppen ansehen',
    'sharing:write': 'Reisefreigaben und Gruppen anlegen, bearbeiten oder widerrufen',
    'calendar:read': 'Kalender-Feed-URLs und Tokens ansehen',
    'calendar:write': 'Kalender-Feed-Tokens erneuern oder widerrufen',
    'templates:read': 'Reise- und Packlistenvorlagen ansehen',
    'templates:write': 'Reise- und Packlistenvorlagen anlegen oder löschen',
    'travel-docs:read': 'Reisedokumente ansehen (Reisepass, Visum usw.)',
    'travel-docs:write': 'Reisedokumente anlegen, bearbeiten und löschen',
    'doc-links:read': 'Dokumentlinks je Reise ansehen',
    'doc-links:write': 'Dokumentlinks je Reise anlegen, bearbeiten und löschen',
    'fares:read': 'Preisbeobachtungen und Preise ansehen',
    'fares:write': 'Preisbeobachtungen anlegen, bearbeiten und löschen',
    'polls:read': 'Abstimmungen zu Reiseentscheidungen ansehen',
    'polls:write': 'Abstimmungen anlegen und abstimmen',
    'journal:read': 'Reisetagebuch-Einträge ansehen',
    'journal:write': 'Reisetagebuch-Einträge anlegen, bearbeiten und löschen',
    'items:read': 'Wichtige Gegenstände ansehen (Wertsachen, Tracker)',
    'items:write': 'Wichtige Gegenstände anlegen, bearbeiten und löschen',
    'requirements:read': 'Einreisebestimmungen ansehen (Visum, Impfungen)',
    'requirements:write': 'Einreisebestimmungen anlegen, bearbeiten und löschen',
    'home-tasks:read': 'To-dos vor der Abreise ansehen',
    'home-tasks:write': 'To-dos für zu Hause anlegen, abhaken und löschen',
    'medications:read': 'Medikamente für die Reise ansehen',
    'medications:write': 'Medikamente für die Reise anlegen, bearbeiten und löschen',
    'cards:read': 'Zahlungskarten und Vorteile ansehen (keine vollständige Kartennummer)',
    'cards:write': 'Zahlungskarten anlegen, bearbeiten und löschen',
    'loyalty:read': 'Bonusprogramme ansehen (standardmäßig ohne Mitgliedsnummern)',
    'loyalty:write': 'Bonusprogramme anlegen, bearbeiten und löschen',
    'insurance:read': 'Versicherungen ansehen (standardmäßig ohne Policennummern)',
    'insurance:write': 'Versicherungen anlegen, bearbeiten und löschen',
    'contacts:read': 'Notfallkontakte ansehen',
    'contacts:write': 'Notfallkontakte anlegen, bearbeiten und löschen',
    'profile-prefs:read': 'Profileinstellungen ansehen (Zeitzone, Vorlaufzeiten, Währung)',
    'profile-prefs:write': 'Profileinstellungen ändern',
    'notifications:read': 'Benachrichtigungseinstellungen je Kanal ansehen',
    'notifications:write': 'Benachrichtigungseinstellungen je Kanal ändern',
    'user-smtp:read': 'Deine eigene SMTP-Einstellung ansehen (das Passwort sehen nur Admins)',
    'user-smtp:write': 'Deine eigene SMTP-Einstellung setzen oder entfernen',
    'comments:read': 'Kommentare zu Reisen ansehen',
    'comments:write': 'Eigene Kommentare zu Reisen schreiben und löschen',
    'gallery:read': 'Fotogalerien zu Orten und Reisen ansehen',
    'gallery:write': 'Galeriefotos sortieren, beschriften und löschen',
    'search:read': 'Dein gesamtes Konto durchsuchen',
    'private-details:read': 'Private Reisenotizen, Buchungsnummern und Reisedetails ansehen',
    'admin:read': 'Benutzer, Audit-Ereignisse und Systemstatistiken ansehen (nur Admins)',
    'admin:write': 'Benutzer anlegen, bearbeiten, löschen und zurücksetzen (nur Admins)',
    'security:read': 'Deine Sicherheitseinstellungen, Sitzungen, Passkeys und OAuth-Clients ansehen',
    'security:write': 'Sicherheitseinstellungen ändern und Sitzungen oder Zugangsdaten widerrufen',
}

path = sys.argv[1]
src = open(path, encoding='utf-8').read()
rx = re.compile(r"^(\t'([a-z-]+:(?:read|write))': )'([^']*)',?$", re.M)
seen = set()

def sub(m):
    key = m.group(2)
    if key not in DE:
        sys.exit(f'no German description for scope {key}')
    seen.add(key)
    assert "'" not in DE[key]
    trail = ',' if m.group(0).endswith(',') else ''
    return f"{m.group(1)}'{DE[key]}'{trail}"

out = rx.sub(sub, src)
missing = set(DE) - seen
if missing:
    sys.exit(f'scopes in the map but not in the source: {sorted(missing)}')
open(path, 'w', encoding='utf-8').write(out)
print(f'translated {len(seen)} scope descriptions')
