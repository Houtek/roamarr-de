"""Build patch 0013: a default <title> (the instance name) for every page. Run inside src/ with the
lower-numbered patches applied.

Upstream sets no default title: app.html and the root layout have none, so the browser tab shows the
URL on every page except the two that set their own (/login/verify, /trips/[id]/print). The root
layout gets a <title> with data.instanceName (admin-configurable, fallback 'Roamarr'), rendered ONLY
on routes without their own title, so exactly one <title> exists per route: no SSR precedence
question, and client-side navigation never leaves a stale page title behind (Svelte assigns
document.title and does not restore it when a page unmounts).
"""
import re, subprocess

OWN_TITLE_ROUTES = ['/login/verify', '/trips/[id]/print']

# Fail loudly if upstream adds or removes a page-level <title>: the list above must match.
found = sorted(
    '/' + p[len('routes/'):-len('/+page.svelte')] if p != 'routes/+page.svelte' else '/'
    for p in subprocess.run(['grep', '-rl', '--include=+page.svelte', '<title', 'routes'],
                            capture_output=True, text=True).stdout.split()
)
assert found == sorted(OWN_TITLE_ROUTES), f'pages with their own <title> changed: {found}'

path = 'routes/+layout.svelte'
t = open(path, encoding='utf-8').read()
assert "import { page } from '$app/state';" in t, 'layout no longer imports page'
assert t.count('</script>\n') == 1, 'expected exactly one </script> in the root layout'
assert '<title' not in t, 'the root layout already has a <title>'

routes = ', '.join(f"'{r}'" for r in OWN_TITLE_ROUTES)
block = (
    "\n<!-- roamarr-de: default tab title; pages that set their own <title> are excluded -->\n"
    "<svelte:head>\n"
    f"\t{{#if ![{routes}].includes(page.route.id ?? '')}}\n"
    "\t\t<title>{data.instanceName ?? 'Roamarr'}</title>\n"
    "\t{/if}\n"
    "</svelte:head>\n"
)
t = t.replace('</script>\n', '</script>\n' + block, 1)
open(path, 'w', encoding='utf-8').write(t)
print('default title: root layout, excluding', routes)
