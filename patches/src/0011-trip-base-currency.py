"""Build patch 0011 (behaviour fix, not translation): new trips take the owner's default currency.

Upstream `createTrip` stores `base_currency: input.baseCurrency ?? 'USD'`, and the new-trip form has no currency
field, so every trip was USD regardless of the user's setting (verified in the DB: owner default EUR, trip USD).
All creation paths (form, import, e-mail ingestion, templates, copy, MCP) go through createTrip, so the fallback is
fixed there: explicit value, else the owner's default currency, else USD. Existing trips are not changed; their
base currency stays editable on the trip edit page. Run inside src/ with 0001-0010 applied.
"""
p = 'lib/server/repositories/tripsRepo.ts'
t = open(p, encoding='utf-8').read()
reps = [
    ("export function createTrip(ownerId: number, input: CreateTripInput): Trip {",
     "// roamarr-de: default a new trip's base currency to its owner's default currency (upstream: always 'USD').\n"
     "function ownerDefaultCurrency(ownerId: number): string {\n"
     "\tconst [owner] = kit.selectFrom(usersTable).where(kitEq(usersTable.id, kitId(ownerId))).executeSync();\n"
     "\treturn (owner?.default_currency as string | null | undefined) || 'USD';\n"
     "}\n\n"
     "export function createTrip(ownerId: number, input: CreateTripInput): Trip {"),
    ("\t\t\tbase_currency: input.baseCurrency ?? 'USD',",
     "\t\t\tbase_currency: input.baseCurrency ?? ownerDefaultCurrency(ownerId),"),
]
for a, b in reps:
    assert t.count(a) == 1, (a[:70], t.count(a))
    t = t.replace(a, b)
open(p, 'w', encoding='utf-8').write(t)
print('createTrip: base currency defaults to the owner default currency')
