#!/usr/bin/env python3
"""Sincroniza os anúncios da EB Trucks no mobile.de com o feed feeds/mobile-de.json (Seller API).

Por cada viatura do feed: cria o anúncio se não existir, atualiza-o se mudou; apaga no mobile.de os
anúncios criados por este script (internalNumber = matrícula) que já não estão no feed (vendidos).
Anúncios sem internalNumber (feitos à mão no mobile.de) não são tocados — ficam listados no final.

Variáveis de ambiente (no GitHub: Settings → Secrets and variables → Actions):
  MOBILE_DE_USER / MOBILE_DE_PASSWORD   credenciais do utilizador API (pedidas a service@team.mobile.de)
  MOBILE_DE_SELLER                      mobileSellerId (opcional; se houver só um vendedor na conta, é esse)
  MOBILE_DE_FEED                        ficheiro ou URL do feed (por omissão https://ebtrucks-site.pages.dev/feeds/mobile-de.json)
  MOBILE_DE_SANDBOX=1                   usar https://services.sandbox.mobile.de em vez da produção

Uso: python3 tools/mobile_de_push.py [--dry-run] [--sandbox] [--feed ficheiro_ou_url]
     --dry-run mostra o plano (criar/atualizar/apagar) sem escrever nada no mobile.de.
"""
import base64, io, json, os, re, ssl, sys, time, urllib.error, urllib.parse, urllib.request, uuid

PROD, SANDBOX = 'https://services.mobile.de', 'https://services.sandbox.mobile.de'
MIME = 'application/vnd.de.mobile.api+json'
MAX_IMG_BYTES = 2 * 1024 * 1024
PLATE_RE = re.compile(r'^[A-Z0-9]{1,4}[- ]?[A-Z0-9]{2,5}([- ]?[A-Z0-9]{2,5})?$')   # matrículas PT/ES/DE que o feed usa como internalNumber

def opener():
    ctx = ssl.create_default_context()
    ca = os.environ.get('SSL_CERT_FILE') or ('/root/.ccr/ca-bundle.crt' if os.path.exists('/root/.ccr/ca-bundle.crt') else None)
    if ca: ctx.load_verify_locations(ca)
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), urllib.request.ProxyHandler({'https': proxy}) if proxy else urllib.request.ProxyHandler({}))

OP = opener()

class Api:
    def __init__(self, base, user, pwd, dry):
        self.base, self.dry = base, dry
        self.auth = 'Basic ' + base64.b64encode(f'{user}:{pwd}'.encode()).decode()
    def call(self, method, path, body=None, headers=None, raw=None, content_type=None, expect=(200, 201, 204, 303)):
        url = self.base + path
        h = {'Authorization': self.auth, 'Accept': MIME, 'User-Agent': 'ebtrucks-site/1.0'}
        if headers: h.update(headers)
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode('utf8'); h['Content-Type'] = MIME
        elif raw is not None:
            data = raw; h['Content-Type'] = content_type
        req = urllib.request.Request(url, data=data, method=method, headers=h)
        try:
            with OP.open(req, timeout=120) as r:
                txt = r.read().decode('utf8', 'replace')
                return r.status, dict(r.headers), (json.loads(txt) if txt.strip().startswith(('{', '[')) else txt)
        except urllib.error.HTTPError as e:
            txt = e.read().decode('utf8', 'replace')
            if e.code in expect: return e.code, dict(e.headers), txt
            raise RuntimeError(f'{method} {path} -> HTTP {e.code}: {txt[:800]}')
    def get(self, path): return self.call('GET', path)[2]

def load_feed(src):
    if re.match(r'^https?://', src):
        with OP.open(urllib.request.Request(src, headers={'User-Agent': 'ebtrucks-site/1.0'}), timeout=60) as r: return json.loads(r.read().decode('utf8'))
    return json.load(open(src, encoding='utf8'))

def fetch_image(url):
    with OP.open(urllib.request.Request(url, headers={'User-Agent': 'ebtrucks-site/1.0'}), timeout=60) as r: data = r.read()
    if len(data) > MAX_IMG_BYTES:
        from PIL import Image
        im = Image.open(io.BytesIO(data)).convert('RGB'); q = 85
        while True:
            buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q, optimize=True); data = buf.getvalue()
            if len(data) <= MAX_IMG_BYTES or q <= 50: break
            q -= 10; im.thumbnail((int(im.width * 0.85), int(im.height * 0.85)))
    return data

def multipart(fields):
    """fields: lista de (nome, filename, content_type, bytes)."""
    b = uuid.uuid4().hex; out = io.BytesIO()
    for name, fn, ct, data in fields:
        out.write(f'--{b}\r\nContent-Disposition: form-data; name="{name}"; filename="{fn}"\r\nContent-Type: {ct}\r\n\r\n'.encode()); out.write(data); out.write(b'\r\n')
    out.write(f'--{b}--\r\n'.encode())
    return out.getvalue(), f'multipart/form-data; boundary={b}'

def upload_images(api, seller, urls, log):
    refs = []
    for u in urls:
        try:
            data = fetch_image(u)
        except Exception as e:
            log(f'    foto ignorada ({e}): {u}'); continue
        if api.dry: refs.append({'ref': u}); continue
        body, ct = multipart([('image', os.path.basename(urllib.parse.urlsplit(u).path) or 'foto.jpg', 'image/jpeg', data)])
        status, headers, resp = api.call('PUT', f'/seller-api/sellers/{seller}/images', raw=body, content_type=ct)
        ref = None
        if isinstance(resp, dict):
            ref = resp.get('ref') or (resp.get('images') or [{}])[0].get('ref')
        if not ref and headers.get('Location'): ref = headers['Location']
        if ref: refs.append({'ref': ref})
        else: log(f'    resposta inesperada ao carregar foto: {str(resp)[:200]}')
        time.sleep(0.3)
    return refs

def fingerprint(ad):
    keys = ('vehicleClass', 'category', 'make', 'modelDescription', 'firstRegistration', 'constructionYear', 'mileage', 'emissionClass', 'wheelFormula', 'axles', 'gearbox', 'power', 'retarder', 'description')
    fp = {k: ad.get(k) for k in keys}
    p = ad.get('price') or {}
    fp['price'] = (p.get('type'), p.get('consumerPriceGross'))
    fp['nimg'] = len(ad.get('images') or [])
    return fp

def main():
    args = sys.argv[1:]
    dry = '--dry-run' in args
    sandbox = '--sandbox' in args or os.environ.get('MOBILE_DE_SANDBOX') == '1'
    feed_src = args[args.index('--feed') + 1] if '--feed' in args else os.environ.get('MOBILE_DE_FEED', 'https://ebtrucks-site.pages.dev/feeds/mobile-de.json')
    user, pwd = os.environ.get('MOBILE_DE_USER'), os.environ.get('MOBILE_DE_PASSWORD')
    log = lambda s: print(s, flush=True)
    feed = load_feed(feed_src)
    wanted = {a['internalNumber']: a for a in feed['ads']}
    log(f"feed {feed_src}: {len(wanted)} anúncios (gerado {feed.get('geradoEm')}) {'[DRY RUN]' if dry else ''}{' [SANDBOX]' if sandbox else ''}")
    no_price = [k for k, a in wanted.items() if (a.get('price') or {}).get('type') == 'ON_REQUEST']
    if no_price: log(f"  sob consulta (enviados com price.type=ON_REQUEST): {', '.join(no_price)}")
    if not user or not pwd:
        log('Sem MOBILE_DE_USER/MOBILE_DE_PASSWORD: nada enviado. O feed está válido; falta só a ativação da Seller API na conta mobile.de.')
        return 0
    api = Api(SANDBOX if sandbox else PROD, user, pwd, dry)
    sellers = api.get('/seller-api/sellers')
    sl = sellers.get('sellers') if isinstance(sellers, dict) else sellers
    seller = os.environ.get('MOBILE_DE_SELLER')
    if not seller:
        if not sl: raise SystemExit('A conta API não tem vendedores associados.')
        if len(sl) > 1: raise SystemExit('Vários vendedores na conta; indicar MOBILE_DE_SELLER=' + ', '.join(str(s.get('mobileSellerId')) for s in sl))
        seller = str(sl[0].get('mobileSellerId'))
    log(f'vendedor mobile.de: {seller}')
    listing = api.get(f'/seller-api/sellers/{seller}/ads')
    remote = listing.get('ads') if isinstance(listing, dict) else listing
    remote = remote or []
    by_key = {}; manual = []
    for ad in remote:
        k = (ad.get('internalNumber') or '').strip().upper()
        if k and PLATE_RE.match(k): by_key[k] = ad
        else: manual.append(ad)
    created = updated = deleted = unchanged = 0
    for key, ad in wanted.items():
        key_u = key.strip().upper()
        urls = [i['ref'] for i in ad.get('images') or []]
        body = dict(ad); body.pop('images', None)
        if key_u in by_key:
            cur = by_key[key_u]; mid = cur.get('mobileAdId')
            cur_imgs = cur.get('images') or []
            same = fingerprint({**cur}) == fingerprint({**ad, 'images': cur_imgs}) and len(cur_imgs) == len(urls)
            if same:
                unchanged += 1; continue
            log(f'  atualizar {key} (mobileAdId {mid})')
            body['images'] = cur_imgs if len(cur_imgs) == len(urls) and cur_imgs else upload_images(api, seller, urls, log)
            if not dry: api.call('PUT', f'/seller-api/sellers/{seller}/ads/{mid}', body=body)
            updated += 1
        else:
            log(f'  criar {key}: {ad.get("make")} {ad.get("modelDescription")} ({len(urls)} fotos)')
            body['images'] = upload_images(api, seller, urls, log)
            if not dry:
                status, headers, resp = api.call('POST', f'/seller-api/sellers/{seller}/ads', body=body, headers={'X-Mobile-Insertion-Request-Id': uuid.uuid4().hex})
                log(f'    -> {status} {headers.get("Location", "")}')
            created += 1
        time.sleep(0.5)
    for key_u, cur in by_key.items():
        if key_u not in {k.strip().upper() for k in wanted}:
            log(f'  apagar {key_u} (mobileAdId {cur.get("mobileAdId")}) — já não está à venda')
            if not dry: api.call('DELETE', f'/seller-api/sellers/{seller}/ads/{cur.get("mobileAdId")}')
            deleted += 1
    log(f'resumo: criados {created}, atualizados {updated}, apagados {deleted}, sem alterações {unchanged}, feitos à mão (não tocados) {len(manual)}')
    for ad in manual:
        log(f'    manual: mobileAdId {ad.get("mobileAdId")} {ad.get("make")} {ad.get("modelDescription")}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
