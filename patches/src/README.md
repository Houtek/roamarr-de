# Patch generators

The `.patch` files one level up form an ordered series. Each was generated against upstream at `UPSTREAM_REF` **plus all lower-numbered patches**. After an upstream bump, a patch that no longer applies can be regenerated from its script instead of by hand:

```bash
git clone https://github.com/visorcraft/Roamarr.git up && git -C up checkout --detach "$(cat UPSTREAM_REF)"
for p in patches/000[1-4]-*.patch; do git -C up apply "$p"; done   # everything below the one to rebuild
git -C up add -A && git -C up commit -qm base
(cd up/src && python3 ../../patches/src/0005-plurals.py)
git -C up add -A && git -C up diff --cached --output=patches/0005-plurals.patch
```

Every script asserts that each exact upstream snippet it rewrites is still present, so an upstream change fails loudly rather than being skipped.

| Patch | Generator |
|---|---|
| 0001 nav labels | none yet: the diff is small (import + 5 render sites + `src/lib/navDe.ts`); edit by hand |
| 0002 scope descriptions | `0002-scope-descriptions.py src/lib/oauthScopes.ts` (takes the file path) |
| 0003 derived labels | none yet: 3 one-line edits in `src/routes/trips/[id]/+page.svelte` |
| 0004 grid pagination | none yet: 8 one-line edits in `src/lib/components/GridTable.svelte` |
| 0005 plurals | `0005-plurals.py` |
| 0006 currency defaults | `0006-currency-defaults.py` |
| 0007 country names | `0007-country-names.py` |
| 0008 visited places | `0008-visited-places.py` |
