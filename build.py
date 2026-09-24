#!/usr/bin/env python3
"""Gera o site estático EB Trucks a partir de stock.json + fotos.
Uso: python3 build.py <pasta_dados> <pasta_saida> [ficheiro_linguas.json]
"""
import json, os, re, sys, shutil, html, unicodedata, datetime
from PIL import Image, ImageOps

SRC, OUT = sys.argv[1], sys.argv[2]
LANGS_FILE = sys.argv[3] if len(sys.argv) > 3 else None
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://ebtrucks.com'
LANGS = ['pt', 'en', 'fr', 'es']

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:70]

def text_of(h):
    if not h: return ''
    t = re.sub(r'<[^>]+>', ' ', h); t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()

stock_en = json.load(open(os.path.join(SRC, 'stock.json'), encoding='utf8'))
by_lang = {'en': {str(v['id']): v for v in stock_en}}
if LANGS_FILE and os.path.exists(LANGS_FILE):
    maps = json.load(open(LANGS_FILE, encoding='utf8'))   # {lingua: {texto_en: traducao}}
    def tr(o, m, key=None):
        if isinstance(o, str): return o if key in ('description', 'model', 'ref', 'slug', 'color', 'register_date') else m.get(o, o)
        if isinstance(o, list): return [tr(x, m, key) for x in o]
        if isinstance(o, dict): return {k: (x if k == 'photos' else tr(x, m, k)) for k, x in o.items()}
        return o
    for l, m in maps.items(): by_lang[l] = {str(v['id']): tr(v, m) for v in stock_en}

os.makedirs(OUT, exist_ok=True)
for d in ('assets', 'v', 'thumbs', 'fotos', 'logo'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

# ---------- fotos + miniaturas ----------
for v in stock_en:
    for p in v['photos']:
        src = os.path.join(SRC, p); dst = os.path.join(OUT, p)
        th = os.path.join(OUT, p.replace('fotos/', 'thumbs/', 1))
        os.makedirs(os.path.dirname(dst), exist_ok=True); os.makedirs(os.path.dirname(th), exist_ok=True)
        if not os.path.exists(dst): shutil.copy2(src, dst)
        if not os.path.exists(th):
            im = ImageOps.exif_transpose(Image.open(src)).convert('RGB'); im.thumbnail((520, 520))
            im.save(th, 'JPEG', quality=78, optimize=True, progressive=True)
for f in os.listdir(os.path.join(SRC, 'logo')):
    shutil.copy2(os.path.join(SRC, 'logo', f), os.path.join(OUT, 'logo', f))
# barra PRR mais leve
bar = Image.open(os.path.join(SRC, 'logo', 'barra_logos_prr.png')); bar.thumbnail((1200, 400)); bar.save(os.path.join(OUT, 'logo', 'barra_prr.png'), optimize=True)
lg = Image.open(os.path.join(SRC, 'logo', 'logo.png')); lg.thumbnail((512, 512)); lg.save(os.path.join(OUT, 'logo', 'logo-512.png'), optimize=True)

os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
PG = os.path.join(SRC, 'paginas')
# imagem principal: DAF à frente do pavilhão, com degradê para o texto (gerada a partir da foto original)
hero_src = os.path.join(SRC, 'fotos', '216', '01_1430.jpg')
if os.path.exists(os.path.join(PG, 'hero_eb.jpg')): shutil.copy2(os.path.join(PG, 'hero_eb.jpg'), os.path.join(OUT, 'img', 'hero.jpg'))
elif os.path.exists(hero_src):
    im = Image.open(hero_src).convert('RGB'); w, h = im.size; c = im.crop((0, 0, w, int(h * 0.9))); H = 820; c = c.resize((int(c.width * H / c.height), H)); W = 2000
    canvas = Image.new('RGB', (W, H), (10, 11, 14)); x = W - c.width; mask = Image.new('L', c.size, 255); fade = 520
    for i in range(fade): mask.paste(int(255 * (i / fade) ** 1.5), (i, 0, i + 1, H))
    canvas.paste(c, (x, 0), mask); canvas.save(os.path.join(OUT, 'img', 'hero.jpg'), quality=82, optimize=True, progressive=True)
p = Image.open(os.path.join(PG, 'premios.png')).convert('RGBA'); p.thumbnail((1600, 1600)); p.save(os.path.join(OUT, 'img', 'premios.png'), optimize=True)
q = Image.open(os.path.join(PG, 'prr_poster.jpg')); q.thumbnail((1200, 1700)); q.save(os.path.join(OUT, 'img', 'prr-poster.jpg'), quality=82, optimize=True)

# ---------- dados por língua ----------
slugs = {}
for v in stock_en:
    title = f"{(v.get('brand') or {}).get('name','')} {v.get('model','')}".strip()
    slugs[v['id']] = f"{v['id']}-{slugify(title)}"
for l in LANGS:
    src = by_lang.get(l) or by_lang['en']
    arr = []
    for v in stock_en:
        o = dict(src.get(str(v['id'])) or v)
        o['photos'] = v['photos']; o['slug'] = slugs[v['id']]
        for k in ('phone', 'email', 'image', 'gallery'): o.pop(k, None)
        arr.append(o)
    with open(os.path.join(OUT, 'assets', f'stock-{l}.js'), 'w', encoding='utf8') as f:
        f.write('window.STOCK=' + json.dumps(arr, ensure_ascii=False, separators=(',', ':')) + ';')

shutil.copy2(os.path.join(HERE, 'style.css'), os.path.join(OUT, 'assets', 'style.css'))
shutil.copy2(os.path.join(HERE, 'app.js'), os.path.join(OUT, 'assets', 'app.js'))

body = open(os.path.join(HERE, 'body_proto.html'), encoding='utf8').read()
VER = datetime.datetime.utcnow().strftime('%Y%m%d%H%M')

def page(base, title, desc, url, image, extra_head='', vid=None, static='', pg=None):
    b = body.replace('{BASE}', base).replace('<main id="app"></main>', f'<main id="app">{static}</main>')
    e = html.escape
    return f'''<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:site_name" content="EB Trucks">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(image)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{base}logo/logo-512.png">
<link rel="stylesheet" href="{base}assets/style.css?v={VER}">
{extra_head}</head>
<body>
{b}
<script>
window.BASE={json.dumps(base)};{f"window.VID={vid};" if vid else ""}{f"window.PAGE={json.dumps(pg)};" if pg else ""}
(function(){{var L=['pt','en','fr','es'],q=new URLSearchParams(location.search).get('lang'),s=null;try{{s=localStorage.getItem('eb_lang')}}catch(e){{}}
var l=q||s||(navigator.language||'pt').slice(0,2);if(L.indexOf(l)<0)l='en';if(q){{try{{localStorage.setItem('eb_lang',l)}}catch(e){{}}}}window.EB_LANG=l;
function add(src,cb){{var t=document.createElement('script');t.src=src;t.onload=cb;document.body.appendChild(t);}}
add(window.BASE+'assets/stock-'+l+'.js?v={VER}',function(){{add(window.BASE+'assets/app.js?v={VER}');}});}})();
</script>
</body>
</html>
'''

# ---------- páginas ----------
pt = by_lang.get('pt') or by_lang['en']
home_desc = 'EB Trucks: venda e exportação de tratores, camiões e semi-reboques usados. Mais de 20 anos de experiência. Mozelos, Santa Maria da Feira, Portugal.'
first_img = f"{SITE}/{stock_en[0]['photos'][0]}" if stock_en and stock_en[0]['photos'] else f'{SITE}/logo/logo-512.png'
org_ld = {"@context": "https://schema.org", "@type": "AutoDealer", "name": "EB Trucks", "url": SITE, "telephone": "+351912502690", "email": "info@ebtrucks.com",
          "address": {"@type": "PostalAddress", "streetAddress": "Rua Central da Vergada, Nº 1550", "postalCode": "4535-166", "addressLocality": "Mozelos", "addressCountry": "PT"}}
static_list = '<noscript><ul>' + ''.join(f'<li><a href="v/{slugs[v["id"]]}.html">{html.escape((v.get("brand") or {}).get("name","")+" "+v.get("model",""))}</a></li>' for v in sorted(stock_en, key=lambda x: -x['id'])) + '</ul></noscript>'
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf8').write(
    page('', 'EB Trucks — Camiões, tratores e semi-reboques usados | Portugal', home_desc, SITE + '/', first_img,
         f'<script type="application/ld+json">{json.dumps(org_ld, ensure_ascii=False)}</script>\n', static=static_list))

urls = [SITE + '/']
redirects = ['/products /index.html 301', '/contactos /index.html#contact 301']
for v in stock_en:
    p = pt.get(str(v['id'])) or v
    title = f"{(v.get('brand') or {}).get('name','')} {v.get('model','')}".strip()
    year = ((v.get('characteristics') or {}).get('register_date') or '')[:4]
    price = f"{v['price']:,}".replace(',', ' ') + ' EUR' if v.get('price') else 'Preço sob consulta'
    bits = [x for x in [(p.get('category') or {}).get('name'), year, price, text_of(v.get('description'))] if x]
    desc = (' · '.join(bits))[:280]
    img = f"{SITE}/{v['photos'][0]}" if v['photos'] else f'{SITE}/logo/logo-512.png'
    url = f"{SITE}/v/{slugs[v['id']]}.html"
    ld = {"@context": "https://schema.org", "@type": "Vehicle", "name": title, "sku": str(v.get('ref') or v['id']), "brand": (v.get('brand') or {}).get('name'),
          "image": [f"{SITE}/{x}" for x in v['photos'][:6]], "description": text_of(v.get('description')) or title, "url": url}
    if year: ld["vehicleModelDate"] = year
    km = (v.get('characteristics') or {}).get('kms')
    if km: ld["mileageFromOdometer"] = {"@type": "QuantitativeValue", "value": km, "unitCode": "KMT"}
    if v.get('price'): ld["offers"] = {"@type": "Offer", "price": v['price'], "priceCurrency": "EUR", "availability": "https://schema.org/InStock", "url": url}
    static = f'<div class="wrap"><h1>{html.escape(title)}</h1><p>{html.escape(desc)}</p></div>'
    open(os.path.join(OUT, 'v', f"{slugs[v['id']]}.html"), 'w', encoding='utf8').write(
        page('../', f'{title} — EB Trucks', desc, url, img, f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n', vid=v['id'], static=static))
    urls.append(url); redirects.append(f"/product/{v['id']} /v/{slugs[v['id']]}.html 301")


# ---------- páginas de conteúdo ----------
CONTENT = json.load(open(os.path.join(HERE, 'paginas.json'), encoding='utf8'))
for pg in CONTENT:
    heads = ''.join(f'<span data-l="{l}">{html.escape(tt)}</span>' for l, tt in pg['title'].items())
    static = f'<div class="phead"><div class="wrap"><h1>{heads}</h1></div></div><div class="wrap prose">' + ''.join(
        f'<div data-l="{blk["langs"]}">{blk["html"]}</div>' for blk in pg['blocks']) + '</div>'
    url = f"{SITE}/{pg['file']}"
    open(os.path.join(OUT, pg['file']), 'w', encoding='utf8').write(
        page('', pg['title']['pt'] + ' — EB Trucks', pg['desc'], url, f"{SITE}/img/{pg['image']}", pg=pg['id'], static=static))
    urls.append(url)
redirects += ['/sobre_nos /sobre-nos.html 301', '/premios /premios.html 301', '/prr /prr.html 301', '/posts/* /prr.html 301']

today = datetime.date.today().isoformat()
open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls) + '</urlset>\n')
open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nDisallow:\n\nSitemap: {SITE}/sitemap.xml\n')
open(os.path.join(OUT, '_redirects'), 'w').write('\n'.join(redirects) + '\n/product/* /index.html 302\n')
open(os.path.join(OUT, '_headers'), 'w').write('''/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'self'
/fotos/*
  Cache-Control: public, max-age=31536000, immutable
/thumbs/*
  Cache-Control: public, max-age=31536000, immutable
''')
open(os.path.join(OUT, '404.html'), 'w', encoding='utf8').write(
    page('/', 'Página não encontrada — EB Trucks', 'Página não encontrada.', SITE + '/404', first_img,
         '<meta name="robots" content="noindex">\n'))
print('veículos', len(stock_en), 'páginas', len(urls), 'línguas', list(by_lang))
