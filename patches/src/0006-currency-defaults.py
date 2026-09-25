"""Build patch 0006 (currency defaults). Run inside src/ of a tree that already has patches 0001-0005."""
HELPER = """// roamarr-de: prefill currency inputs with the signed-in user's default currency instead of a
// hardcoded 'USD'. The root layout puts the user (incl. defaultCurrency) into every page's data.
export function defaultCurrency(pageData: Record<string, unknown> | undefined | null): string {
\tconst user = pageData?.user as { defaultCurrency?: string | null } | null | undefined;
\treturn user?.defaultCurrency || 'USD';
}
"""
open('lib/defaultCurrency.ts', 'w').write(HELPER)
IMP = "<script lang=\"ts\">\n\timport { page as __page } from '$app/state';\n\timport { defaultCurrency } from '$lib/defaultCurrency';\n"
edits = {
    'routes/insurance/new/+page.svelte': [("value={form?.values?.currency ?? 'USD'}", "value={form?.values?.currency ?? defaultCurrency(__page.data)}")],
    'routes/cards/[id]/edit/+page.svelte': [("value={(addBenefitValues?.currency as string | undefined) ?? 'USD'}", "value={(addBenefitValues?.currency as string | undefined) ?? defaultCurrency(__page.data)}")],
    'routes/trips/[id]/+page.svelte': [('<input name="currency" class="input text-sm" value="USD" placeholder="USD" required />', '<input name="currency" class="input text-sm" value={defaultCurrency(__page.data)} placeholder="USD" required />')],
    'routes/trips/[id]/edit/+page.svelte': [("value={data.trip.baseCurrency ?? 'USD'}", "value={data.trip.baseCurrency ?? defaultCurrency(__page.data)}")],
}
for p, reps in edits.items():
    t = open(p, encoding='utf-8').read()
    assert t.startswith('<script lang="ts">\n'), p
    for a, b in reps:
        assert t.count(a) == 1, (p, a, t.count(a))
        t = t.replace(a, b)
    t = t.replace('<script lang="ts">\n', IMP, 1)
    open(p, 'w', encoding='utf-8').write(t)
print('currency defaults: 4 forms + helper')
