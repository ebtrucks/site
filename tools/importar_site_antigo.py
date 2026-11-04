#!/usr/bin/env python3
"""Importa o stock do site antigo (ebtrucks.com, Laravel) para dados/stock.json + dados/fotos/.

Enquanto o site antigo for o sítio onde se carregam fotos e anúncios, este script mantém o
repositório (site novo + feeds) em dia:
  - veículos novos no site antigo → entram em stock.json e as fotos são descarregadas (máx. 1600 px);
  - veículos já conhecidos → campos de catálogo atualizados a partir da API; fotos só se a galeria mudou;
  - veículos que desapareceram do site antigo → ficam em stock.json com "no_site_antigo": false
    (o estado do artefacto, em dados/estado.json, é que decide se aparecem no site e nos feeds).
Campos que a API não tem (description_i18n, video, video_url, descricao_manual) são preservados.

Uso: python3 tools/importar_site_antigo.py [pasta_dados]   (por omissão: dados)
Sai com código 0; imprime um resumo. Não precisa de credenciais: a API pública do site antigo chega.
"""
import io, json, os, re, ssl, sys, time, urllib.parse, urllib.request
from PIL import Image, ImageOps

API = 'https://ebtrucks.com/api/products'
HEADERS = {'Accept': 'application/json', 'Accept-Language': 'en', 'User-Agent': 'ebtrucks-site/1.0 (+https://ebtrucks.com)'}
MAX_PX = 1600
KEEP = ('description_i18n', 'video', 'video_url', 'descricao_manual', 'matricula')

def opener():
    ctx = ssl.create_default_context()
    ca = os.environ.get('SSL_CERT_FILE') or ('/root/.ccr/ca-bundle.crt' if os.path.exists('/root/.ccr/ca-bundle.crt') else None)
    if ca: ctx.load_verify_locations(ca)
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    handlers = [urllib.request.HTTPSHandler(context=ctx)]
    handlers.append(urllib.request.ProxyHandler({'https': proxy}) if proxy else urllib.request.ProxyHandler({}))
    return urllib.request.build_opener(*handlers)

OP = opener()

def get(url, binary=False, tries=3):
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with OP.open(req, timeout=60) as r:
                data = r.read()
            return data if binary else json.loads(data.decode('utf8'))
        except Exception as e:  # noqa
            if n == tries - 1: raise
            time.sleep(2 + 2 * n)

def list_ids():
    ids, page = [], 1
    while True:
        d = get(f'{API}?per_page=50&page={page}')
        ps = d['data']['products']; ids += [p['id'] for p in ps]
        pg = d['data'].get('pagination') or {}
        if not ps or page >= int(pg.get('last_page') or 1): break
        page += 1
    return ids

def gallery_of(p):
    """Capa (image) primeiro e depois a galeria, sem repetir a mesma fotografia (mesmo nome de ficheiro)."""
    out, seen = [], set()
    for x in [p.get('image')] + list(p.get('gallery') or []):
        if not x or not x.get('url'): continue
        key = ((x.get('file_name') or '').lower(), x.get('size')) if x.get('file_name') else x.get('id')
        if key in seen: continue
        seen.add(key); out.append(x)
    return out

def photo_ids_in_dir(d):
    out = []
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            m = re.match(r'^\d+_(\d+)\.jpe?g$', f, re.I)
            if m: out.append(int(m.group(1)))
    return out

def download_photos(p, dest_dir):
    """Descarrega a galeria para dest_dir como NN_<id>.jpg (reduzidas). Devolve a lista de caminhos relativos."""
    g = gallery_of(p)
    os.makedirs(dest_dir, exist_ok=True)
    for f in os.listdir(dest_dir):  # galeria mudou: recomeça
        os.remove(os.path.join(dest_dir, f))
    rel = []
    for n, img in enumerate(g, 1):
        name = f"{n:02d}_{img.get('id', n)}.jpg"
        raw = get(img['url'], binary=True)
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB')
        im.thumbnail((MAX_PX, MAX_PX))
        im.save(os.path.join(dest_dir, name), 'JPEG', quality=85, optimize=True, progressive=True)
        rel.append(f"{os.path.basename(dest_dir)}/{name}")
        time.sleep(0.2)
    return [f'fotos/{r}' for r in rel]

def api_to_entry(p):
    e = {k: p.get(k) for k in ('id', 'ref', 'description', 'brand', 'model', 'price', 'category', 'is_featured', 'condition',
                                 'motor_details', 'characteristics', 'sub_category', 'phone', 'email', 'generic_details', 'body_details')}
    e['price'] = int(e['price'] or 0)
    return e

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dados')
    path = os.path.join(src, 'stock.json')
    stock = json.load(open(path, encoding='utf8')) if os.path.exists(path) else []
    by_id = {v['id']: v for v in stock}
    ids = list_ids()
    novos, atualizados, fotos_novas = [], [], []
    for i in ids:
        p = get(f'{API}/{i}')['data']['product']
        new = api_to_entry(p)
        old = by_id.get(i)
        if old:
            for k in KEEP:
                if k in old: new[k] = old[k]
            if old.get('descricao_manual'): new['description'] = old.get('description')
            new['photos'] = old.get('photos') or []
            gal = [x.get('id') for x in gallery_of(p) if x.get('id')]
            have = photo_ids_in_dir(os.path.join(src, 'fotos', str(i)))
            if gal and set(have) != set(gal):   # galeria mudou (ou fotos em falta) → descarregar de novo
                new['photos'] = download_photos(p, os.path.join(src, 'fotos', str(i))); fotos_novas.append(i)
            if {k: v for k, v in new.items() if k not in ('importado_em', 'no_site_antigo')} != {k: v for k, v in old.items() if k not in ('importado_em', 'no_site_antigo')}:
                atualizados.append(i)
        else:
            new['photos'] = download_photos(p, os.path.join(src, 'fotos', str(i))); fotos_novas.append(i); novos.append(i)
        new['no_site_antigo'] = True
        new['importado_em'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        by_id[i] = new
    desaparecidos = []
    for i, v in by_id.items():
        if i not in ids and v.get('no_site_antigo', True):
            v['no_site_antigo'] = False; desaparecidos.append(i)
    out = sorted(by_id.values(), key=lambda v: -v['id'])
    with open(path, 'w', encoding='utf8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1); f.write('\n')
    print(f"site antigo: {len(ids)} veículos; stock.json: {len(out)} | novos {novos} | atualizados {atualizados} | fotos {fotos_novas} | já não estão no site antigo {desaparecidos}")

if __name__ == '__main__':
    main()
