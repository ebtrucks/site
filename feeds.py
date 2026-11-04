#!/usr/bin/env python3
"""Feeds para os portais (mobile.de, Autoline, Europa-Camiões, trucks.nl, CustoJusto…).

Junta duas fontes:
  - dados/stock.json   — conteúdo dos anúncios (título, descrição, fotos, preço de tabela)
  - dados/estado.json  — instantâneo do artefacto «Ebtrucks Stock» (estado, preço, km, ano…)
e produz em <saída>/feeds/:
  stock.xml       feed genérico (todas as viaturas à venda, com fotos em URL absoluto)
  stock.csv       o mesmo em CSV (; como separador, UTF-8 com BOM)
  mobile-de.json  anúncios já no formato da Seller API do mobile.de
  relatorio.json  o que entrou, o que ficou de fora e porquê
  index.html      a mesma informação legível

Uso isolado:  python3 feeds.py <pasta_dados> <pasta_saida> [url_base]
No build.py é chamado com os mesmos dados, para que o site e os feeds digam o mesmo.
"""
import csv, datetime, html, io, json, os, re, sys, unicodedata
from xml.sax.saxutils import escape as xesc, quoteattr

SITE_CANONICO = 'https://ebtrucks.com'
VENDEDOR = {
    'nome': 'EB Trucks (E.B., Lda)', 'nif': '507173406',
    'morada': 'Rua Central da Vergada, 1550', 'codigoPostal': '4535-166',
    'localidade': 'Mozelos, Santa Maria da Feira', 'pais': 'PT',
    'telefone': '+351912502690', 'email': 'info@ebtrucks.com', 'site': SITE_CANONICO,
}
A_VENDA = ('Disponível', 'Reservado')

# ---------------------------------------------------------------- utilidades

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:70]

def text_of(h):
    """HTML -> texto simples com quebras de linha entre parágrafos."""
    if not h: return ''
    t = re.sub(r'(?i)</(p|div|li|h[1-6]|tr)>|<br\s*/?>', '\n', h)
    t = re.sub(r'<[^>]+>', ' ', t); t = html.unescape(t)
    t = re.sub(r'[ \t\xa0]+', ' ', t)
    t = '\n'.join(line.strip() for line in t.split('\n'))
    return re.sub(r'\n\n+', '\n', t).strip()

def plate_comps(p):
    """'R-1654-BBZ' -> ['R','1654','BBZ'];  '2945JGY' -> ['2945','JGY']."""
    out = []
    for x in re.split(r'[^A-Z0-9]+', str(p or '').upper()):
        if not x: continue
        if re.search(r'[A-Z]', x) and re.search(r'[0-9]', x):
            out += re.findall(r'[A-Z]+|[0-9]+', x)
        else:
            out.append(x)
    return out

def plate_key(p):
    return ''.join(plate_comps(p))

def ref_matches_plate(ref, plate):
    r, c = plate_comps(ref), plate_comps(plate)
    if not r or not c: return False
    return any(c[i:i + len(r)] == r for i in range(len(c) - len(r) + 1))

def site_title(v):
    b, m = (v.get('brand') or {}).get('name', '') or '', v.get('model', '') or ''
    return m.strip() if b and m.upper().startswith(b.upper() + ' ') else f"{b} {m}".strip()

def site_slug(v):
    return f"{v['id']}-{slugify(site_title(v))}"

# ---------------------------------------------------------------- normalização

EURO_RE = re.compile(r'(?i)euro\s*(VI|V|IV|III|II|I|[1-7])\s*([a-z])?')
ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6}

def euro_norm(s):
    """'Euro VI D' -> ('6','D'); 'Euro 4/5' -> ('5',''); 6 -> ('6','')."""
    if s is None or s == '': return ('', '')
    s = str(s)
    m = list(EURO_RE.finditer(s))
    if not m:
        return (s.strip(), '') if re.fullmatch(r'[1-7]', s.strip()) else ('', '')
    last = m[-1]
    n = last.group(1).upper(); n = str(ROMAN.get(n, n))
    return (n, (last.group(2) or '').upper())

def axles_norm(s, category):
    """Devolve (formula_rodas, n_eixos).  '4x2' -> ('4x2', 2); '3 eixos' -> ('', 3); '3 eixos (6x2)' -> ('6x2', 3)."""
    s = str(s or '')
    m = re.search(r'(\d)\s*[xX×]\s*(\d)', s)
    formula = f'{m.group(1)}x{m.group(2)}' if m else ''
    n = None
    m2 = re.search(r'(\d+)\s*eixo', s, re.I)
    if m2: n = int(m2.group(1))
    elif formula: n = int(formula[0]) // 2
    return formula, n

def gearbox_norm(s):
    s = (s or '').lower()
    if not s: return ''
    if 'auto' in s or 'autom' in s: return 'automatica'
    if 'semi' in s: return 'semiautomatica'
    if 'manu' in s: return 'manual'
    return ''

def status_slug(st):
    return {'Disponível': 'disponivel', 'Reservado': 'reservado', 'Vendido': 'vendido',
            'Concluído': 'concluido', 'Em preparação': 'em_preparacao'}.get(st, slugify(st or ''))

def category_norm(cat):
    c = (cat or '').lower()
    if 'trat' in c or 'tract' in c: return 'trator'
    if 'semi' in c: return 'semirreboque'
    if 'rebo' in c or 'trail' in c: return 'reboque'
    if 'cami' in c or 'truck' in c: return 'camiao'
    return slugify(cat or 'outro') or 'outro'

TIPO_EN = {'trator': 'tractor_unit', 'camiao': 'truck', 'semirreboque': 'semi_trailer', 'reboque': 'trailer', 'outro': 'other'}

# ---------------------------------------------------------------- dados

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, encoding='utf8') as f: return json.load(f)
    return default

def load_estado(src):
    e = load_json(os.path.join(src, 'estado.json'), {}) or {}
    by_plate = {}
    for r in e.get('viaturas') or []:
        if r.get('plate'): by_plate[plate_key(r['plate'])] = r
    e['_by_plate'] = by_plate
    return e

def a_venda(rec):
    return bool(rec) and rec.get('status') in A_VENDA and rec.get('dest') != 'Para peças'

def match_site_to_estado(stock, estado, ligacoes):
    """{site_id: registo do artefacto ou None}. ligacoes = {site_id(str): matrícula} força a ligação."""
    out = {}
    recs = list(estado.get('_by_plate', {}).values())
    for v in stock:
        forced = (ligacoes or {}).get(str(v['id']))
        if forced:
            out[v['id']] = estado['_by_plate'].get(plate_key(forced)); continue
        ref = str(v.get('ref') or '')
        hits = [r for r in recs if ref_matches_plate(ref, r['plate'])]
        # a mesma matrícula pode aparecer duas vezes (duplicado no site): fica o primeiro
        out[v['id']] = hits[0] if len({plate_key(h['plate']) for h in hits}) == 1 else None
    return out

def merged_items(stock, estado, ligacoes, subtipos, base_url):
    """Devolve (itens à venda para os feeds, relatório)."""
    link = match_site_to_estado(stock, estado, ligacoes)
    by_plate_site = {}
    for v in stock:
        r = link.get(v['id'])
        if r: by_plate_site.setdefault(plate_key(r['plate']), []).append(v)
    items, rel = [], {'incluidos': [], 'reservados': [], 'sem_fotos_no_site': [], 'sem_registo_no_artefacto': [],
                      'ocultos_por_estado': [], 'duplicados_no_site': []}
    seen = set()
    for v in sorted(stock, key=lambda x: -x['id']):
        r = link.get(v['id'])
        if not r:
            rel['sem_registo_no_artefacto'].append({'siteId': v['id'], 'ref': v.get('ref'), 'titulo': site_title(v), 'noSiteAntigo': v.get('no_site_antigo')})
            continue
        pk = plate_key(r['plate'])
        if not a_venda(r):
            rel['ocultos_por_estado'].append({'siteId': v['id'], 'plate': r['plate'], 'status': r.get('status'), 'dest': r.get('dest'), 'titulo': site_title(v)})
            continue
        if pk in seen:
            rel['duplicados_no_site'].append({'siteId': v['id'], 'plate': r['plate']}); continue
        seen.add(pk)
        if not v.get('photos'):
            rel['sem_fotos_no_site'].append({'siteId': v['id'], 'plate': r['plate'], 'titulo': site_title(v)}); continue
        items.append(build_item(v, r, subtipos, base_url))
    # viaturas à venda no artefacto que não têm anúncio no site (sem fotos públicas)
    for r in estado.get('viaturas') or []:
        if a_venda(r) and plate_key(r['plate']) not in by_plate_site:
            rel['sem_fotos_no_site'].append({'plate': r['plate'], 'stockNo': r.get('stockNo'), 'titulo': f"{r.get('make','')} {r.get('model','')}".strip(), 'status': r.get('status')})
    rel['incluidos'] = [{'id': i['id'], 'ref': i['ref'], 'siteId': i['siteId'], 'titulo': i['titulo'], 'preco': i['preco'], 'estado': i['estado'], 'fotos': len(i['fotos'])} for i in items]
    rel['reservados'] = [i['id'] for i in items if i['estado'] == 'reservado']
    return items, rel

def build_item(v, r, subtipos, base_url):
    ch, mo, gd, bd = (v.get('characteristics') or {}), (v.get('motor_details') or {}), (v.get('generic_details') or {}), (v.get('body_details') or {})
    cat = category_norm(r.get('category') or (v.get('category') or {}).get('name'))
    make = (r.get('make') or (v.get('brand') or {}).get('name') or '').strip()
    model = (r.get('model') or '').strip()
    if not model or model == '—': model = (v.get('model') or '').strip()
    reg = (ch.get('register_date') or '')[:7]
    year = r.get('year') or (int(reg[:4]) if reg[:4].isdigit() else None)
    price = r.get('price') if isinstance(r.get('price'), (int, float)) and r.get('price') > 0 else (v.get('price') if (v.get('price') or 0) > 0 else None)
    km = r.get('km') if isinstance(r.get('km'), (int, float)) and r.get('km') > 0 else (ch.get('kms') if (ch.get('kms') or 0) > 0 else None)
    euro_n, euro_v = euro_norm(r.get('euro') if r.get('euro') not in (None, '') else mo.get('euro'))
    formula, n_axles = axles_norm(r.get('axles') or gd.get('axles_configuration') or '', cat)
    if not n_axles and (gd.get('axles_number') or 0) > 0: n_axles = gd['axles_number']
    title_site = site_title(v)
    desc_i18n = v.get('description_i18n') or {}
    descs = {l: text_of(d) for l, d in desc_i18n.items() if text_of(d)}
    if 'pt' not in descs and v.get('description'): descs['pt'] = text_of(v['description'])
    titulo = f"{make} {model}".strip() or title_site
    if year and str(year) not in titulo: titulo_long = f"{titulo}, {year}"
    else: titulo_long = titulo
    retarder = bool(bd.get('retarder')) or bool(re.search(r'(?i)\bret(arder)?\b', v.get('model') or ''))
    return {
        'id': r['plate'], 'ref': r.get('stockNo') or '', 'siteId': v['id'],
        'estado': status_slug(r.get('status')), 'tipo': cat, 'tipoEn': TIPO_EN.get(cat, 'other'),
        'subtipo': (subtipos or {}).get(str(v['id'])) or '', 'carrocaria': r.get('body') or '',
        'marca': make, 'modelo': model, 'titulo': titulo_long, 'tituloSite': title_site,
        'descricoes': descs, 'preco': price, 'moeda': 'EUR',
        'ano': year, 'primeiraMatricula': reg if len(reg) == 7 else '', 'km': km,
        'euro': euro_n, 'euroVariante': euro_v, 'potenciaCv': mo.get('horse_power') or None, 'cilindrada': mo.get('engine_capacity') or None,
        'combustivel': mo.get('fuel') or '', 'caixa': gearbox_norm(mo.get('gearbox_type')), 'retarder': retarder,
        'adr': bool(bd.get('adr')), 'grua': bool(bd.get('crane')), 'plataformaElevatoria': bool(bd.get('platform')),
        'eixos': formula, 'numEixos': n_axles, 'suspensao': ', '.join(gd.get('suspension') or []), 'travoes': gd.get('brake_system') or '',
        'pneus': ch.get('wheel_size') or '', 'dimensoes': bd.get('body_dimensions') or '',
        'matricula': r['plate'], 'localizacao': f"{VENDEDOR['localidade']}, Portugal",
        'fotos': [f"{base_url}/{p}" for p in v.get('photos') or []],
        'url': f"{base_url}/v/{site_slug(v)}.html",
        'atualizadoEm': r.get('updatedAt') or '',
    }

# ---------------------------------------------------------------- saídas

def write_xml(items, path, gerado):
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         f'<stock xmlns="https://ebtrucks.com/feeds" versao="1" geradoEm={quoteattr(gerado)} total="{len(items)}">',
         '  <vendedor>' + ''.join(f'<{k}>{xesc(v)}</{k}>' for k, v in VENDEDOR.items()) + '</vendedor>']
    for i in items:
        L.append(f'  <viatura id={quoteattr(i["id"])} ref={quoteattr(i["ref"])} siteId="{i["siteId"]}">')
        def el(tag, val, **attrs):
            if val is None or val == '' or val is False: return
            a = ''.join(f' {k}={quoteattr(str(v))}' for k, v in attrs.items())
            L.append(f'    <{tag}{a}>{xesc(str(val).lower() if isinstance(val, bool) else str(val))}</{tag}>')
        el('estado', i['estado']); el('reservado', 'true' if i['estado'] == 'reservado' else 'false')
        el('tipo', i['tipo']); el('tipoEn', i['tipoEn']); el('subtipo', i['subtipo']); el('carrocaria', i['carrocaria'])
        el('marca', i['marca']); el('modelo', i['modelo']); el('titulo', i['titulo']); el('tituloSite', i['tituloSite'])
        for l, d in i['descricoes'].items(): el('descricao', d, lang=l)
        if i['preco']: L.append(f'    <preco moeda="EUR">{int(i["preco"])}</preco>')
        else: L.append('    <preco moeda="EUR" sobConsulta="true"/>')
        el('ano', i['ano']); el('primeiraMatricula', i['primeiraMatricula']); el('quilometros', i['km'])
        el('euro', i['euro'] + (i['euroVariante'].lower() if i['euroVariante'] else '') if i['euro'] else '')
        el('potenciaCv', i['potenciaCv']); el('cilindrada', i['cilindrada']); el('combustivel', i['combustivel']); el('caixa', i['caixa'])
        el('retarder', 'true' if i['retarder'] else ''); el('adr', 'true' if i['adr'] else ''); el('grua', 'true' if i['grua'] else ''); el('plataformaElevatoria', 'true' if i['plataformaElevatoria'] else '')
        el('eixos', i['eixos']); el('numEixos', i['numEixos']); el('suspensao', i['suspensao']); el('travoes', i['travoes']); el('pneus', i['pneus']); el('dimensoes', i['dimensoes'])
        el('matricula', i['matricula']); el('localizacao', i['localizacao']); el('pais', 'PT')
        L.append('    <fotos>' + ''.join(f'<foto ordem="{n + 1}">{xesc(u)}</foto>' for n, u in enumerate(i['fotos'])) + '</fotos>')
        el('url', i['url']); el('atualizadoEm', i['atualizadoEm'])
        L.append('  </viatura>')
    L.append('</stock>')
    with open(path, 'w', encoding='utf8') as f: f.write('\n'.join(L) + '\n')

CSV_COLS = ['id', 'ref', 'estado', 'tipo', 'tipoEn', 'subtipo', 'carrocaria', 'marca', 'modelo', 'titulo', 'preco', 'moeda', 'ano', 'primeiraMatricula',
            'km', 'euro', 'potenciaCv', 'caixa', 'retarder', 'adr', 'eixos', 'numEixos', 'matricula', 'localizacao', 'url', 'descricao_pt', 'descricao_en', 'fotos']

def write_csv(items, path):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=';', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    w.writerow(CSV_COLS)
    for i in items:
        row = dict(i); row['descricao_pt'] = i['descricoes'].get('pt', ''); row['descricao_en'] = i['descricoes'].get('en', '')
        row['fotos'] = '|'.join(i['fotos']); row['preco'] = int(i['preco']) if i['preco'] else ''
        row['euro'] = (i['euro'] + i['euroVariante'].lower()) if i['euro'] else ''
        w.writerow(['' if row.get(c) is None else ('sim' if row.get(c) is True else 'nao' if row.get(c) is False else row.get(c)) for c in CSV_COLS])
    with open(path, 'w', encoding='utf-8-sig') as f: f.write(buf.getvalue())

# --- mobile.de (Seller API) -------------------------------------------------
MOBILE_MAKES = {'MERCEDES': 'MERCEDES-BENZ', 'MERCEDES-BENZ': 'MERCEDES-BENZ', 'DAF': 'DAF', 'SCANIA': 'SCANIA', 'VOLVO': 'VOLVO', 'MAN': 'MAN', 'IVECO': 'IVECO',
                'RENAULT': 'RENAULT', 'RENAULT TRUCKS': 'RENAULT', 'KRONE': 'KRONE', 'SCHMITZ': 'SCHMITZ', 'SCHMITZ CARGOBULL': 'SCHMITZ', 'NOOTEBOOM': 'NOOTEBOOM',
                'FRUEHAUF': 'FRUEHAUF', 'FLIEGL': 'FLIEGL', 'KÖGEL': 'KOEGEL', 'KOGEL': 'KOEGEL', 'KOEGEL': 'KOEGEL', 'SAMRO': 'SAMRO', 'MONTENEGRO': 'MONTENEGRO',
                'LECIÑENA': 'LECINENA', 'LECINENA': 'LECINENA', 'SCHEUERLE': 'SCHEUERLE', 'SCHUERLE': 'SCHEUERLE'}
MOBILE_CLASS = {'trator': 'SemiTrailerTruck', 'camiao': 'TruckOver7500', 'semirreboque': 'SemiTrailer', 'reboque': 'Trailer'}
# categoria mobile.de por (classe, subtipo/carroçaria); a chave '' é o valor por omissão da classe
MOBILE_CAT = {
    'SemiTrailerTruck': {'': 'StandardTractorAndTrailerUnit', 'heavy': 'HeavyLoad', 'adr': 'HazardousLoad'},
    'TruckOver7500': {'': 'OtherTruckOver7500', 'furgao': 'BoxTruck', 'lona': 'StakeBodyAndTarpaulinTruck', 'plataforma': 'StakeBodyTruck', 'cisterna': 'TankBodiesTruck',
                      'frigorifico': 'RefrigeratorBodyTruck', 'ampliroll': 'RollOffTipperTruck', 'porta_contentores': 'SwapChassisTruck', 'grua': 'TruckMountedCraneTruck', 'chassis': 'ChassisTruck', 'basculante': 'TipperTruck'},
    'SemiTrailer': {'': 'OtherSemiTrailer', 'lona': 'StakeBodyAndTarpaulinSemiTrailer', 'plataforma': 'PlatformSemiTrailer', 'extensivel': 'LongMaterialTransporterSemiTrailer',
                    'porta_maquinas': 'LowLoaderSemiTrailer', 'cisterna': 'TankBodiesSemiTrailer', 'frigorifico': 'RefrigeratorBodySemiTrailer', 'porta_contentores': 'ChassisSemiTrailer',
                    'caixa_fechada': 'BoxSemiTrailer', 'furgao': 'BoxSemiTrailer', 'basculante': 'TipperSemiTrailer'},
    'Trailer': {'': 'OtherTrailer', 'lona': 'StakeBodyAndTarpaulinTrailer', 'plataforma': 'PlatformTrailer', 'porta_maquinas': 'LowLoaderTrailer', 'cisterna': 'TankBodiesTrailer',
                'frigorifico': 'RefrigeratorBodyTrailer', 'porta_contentores': 'ChassisTrailer', 'furgao': 'BoxTrailer', 'basculante': 'TipperTrailer'},
}

def mobile_category(cls, item):
    sub = item['subtipo'] or ''
    carr = (item['carrocaria'] or '').lower()
    if cls == 'SemiTrailerTruck':
        if item['adr'] or ' adr' in f' {carr}': return 'HazardousLoad'
        if 'especial' in carr or 'pesado' in carr or (item['eixos'] in ('6x4', '8x4')): return 'HeavyLoad'
        return 'StandardTractorAndTrailerUnit'
    table = MOBILE_CAT[cls]
    # 1.º a carroçaria da ficha (artefacto), por palavras-chave, da mais específica para a mais geral
    for k, cat in (('cisterna', 'cisterna'), ('frigor', 'frigorifico'), ('lona', 'lona'), ('cortina', 'lona'), ('furg', 'furgao'), ('caixa fechada', 'caixa_fechada'),
                   ('porta-fatos', 'caixa_fechada'), ('contentor', 'porta_contentores'), ('carga baixa', 'porta_maquinas'), ('porta-máquinas', 'porta_maquinas'), ('rebaix', 'porta_maquinas'),
                   ('grua', 'grua'), ('gancho', 'ampliroll'), ('ampliroll', 'ampliroll'), ('bascul', 'basculante'), ('extens', 'extensivel'), ('chassis', 'chassis'),
                   ('estrado', 'plataforma'), ('plataforma', 'plataforma')):
        if k in carr and cat in table: return table[cat]
    # 2.º o subtipo do site (dados/subtipos.json)
    if sub and sub in table: return table[sub]
    return table['']

def mobile_ad(item):
    cls = MOBILE_CLASS.get(item['tipo'], 'TruckOver7500')
    make = MOBILE_MAKES.get(item['marca'].upper(), 'ANDERE')
    model_desc = (f"{item['marca']} " if make == 'ANDERE' else '') + item['modelo']
    if item['carrocaria'] and item['carrocaria'].lower() not in model_desc.lower(): model_desc += f" · {item['carrocaria']}"
    ad = {'internalNumber': item['id'], 'vehicleClass': cls, 'category': mobile_category(cls, item), 'make': make, 'modelDescription': model_desc[:80], 'condition': 'USED',
          'description': (item['descricoes'].get('de') or item['descricoes'].get('en') or item['descricoes'].get('pt') or item['titulo'])[:5000],
          'images': [{'ref': u} for u in item['fotos'][:30]], 'countryVersion': 'PT'}
    if item['primeiraMatricula']: ad['firstRegistration'] = item['primeiraMatricula'].replace('-', '')
    elif item['ano']: ad['constructionYear'] = int(item['ano'])
    if item['km']: ad['mileage'] = int(item['km'])
    if item['preco']: ad['price'] = {'type': 'FIXED', 'currency': 'EUR', 'consumerPriceGross': int(item['preco'])}
    else: ad['price'] = {'type': 'ON_REQUEST', 'currency': 'EUR'}
    if item['euro']: ad['emissionClass'] = 'EURO' + item['euro'] + (item['euroVariante'] if item['euroVariante'] in ('C', 'D') else '')
    if item['eixos'] and cls in ('SemiTrailerTruck', 'TruckOver7500'): ad['wheelFormula'] = item['eixos'].upper()
    if item['numEixos']: ad['axles'] = int(item['numEixos'])
    if item['caixa'] == 'automatica': ad['gearbox'] = 'AUTOMATIC_GEAR'
    elif item['caixa'] == 'manual': ad['gearbox'] = 'MANUAL_GEAR'
    elif item['caixa'] == 'semiautomatica': ad['gearbox'] = 'SEMIAUTOMATIC_GEAR'
    if item['potenciaCv']: ad['power'] = int(round(item['potenciaCv'] * 0.7355))
    if item['cilindrada']: ad['cubicCapacity'] = int(item['cilindrada'])
    if cls in ('SemiTrailerTruck', 'TruckOver7500'): ad['fuel'] = 'DIESEL'
    if item['retarder']: ad['retarder'] = True
    if item['estado'] == 'reservado': ad['highlights'] = ['Reservado / Reserved']
    return ad

def write_mobile(items, path, gerado):
    doc = {'geradoEm': gerado, 'nota': 'Um anúncio por viatura no formato da Seller API do mobile.de (JSON). tools/mobile_de_push.py envia isto para a conta da EB Trucks.',
           'ads': [mobile_ad(i) for i in items]}
    with open(path, 'w', encoding='utf8') as f: json.dump(doc, f, ensure_ascii=False, indent=1)

def write_report(rel, path_json, path_html, gerado, base_url, estado):
    rel = dict(rel); rel['geradoEm'] = gerado; rel['estadoDoArtefacto'] = (estado or {}).get('geradoEm', '')
    with open(path_json, 'w', encoding='utf8') as f: json.dump(rel, f, ensure_ascii=False, indent=1)
    e = html.escape
    def tbl(rows, cols):
        if not rows: return '<p class="ok">— nada —</p>'
        return '<table><tr>' + ''.join(f'<th>{e(c)}</th>' for c in cols) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{e(str(r.get(c, "") if r.get(c) is not None else ""))}</td>' for c in cols) + '</tr>' for r in rows) + '</table>'
    body = f'''<!DOCTYPE html><html lang="pt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>Feeds para os portais — EB Trucks</title>
<style>body{{font:15px/1.45 system-ui,sans-serif;margin:0;padding:24px;max-width:1100px;color:#18212b}}h1{{font-size:26px;margin:0 0 4px}}h2{{font-size:18px;margin:28px 0 8px}}table{{border-collapse:collapse;width:100%;font-size:13.5px}}th,td{{border-bottom:1px solid #d5dbe2;padding:6px 8px;text-align:left;vertical-align:top}}th{{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:#5b6876}}code{{background:#eef1f4;padding:2px 6px;border-radius:4px}}.ok{{color:#1f8a4c}}.muted{{color:#5b6876}}ul{{padding-left:20px}}</style></head><body>
<h1>Feeds para os portais</h1><p class="muted">Gerado em {e(gerado)} · estado do artefacto de {e(rel['estadoDoArtefacto'] or '—')} · {len(rel['incluidos'])} viaturas no feed</p>
<h2>Endereços a dar aos portais</h2><ul>
<li>XML genérico: <code>{e(base_url)}/feeds/stock.xml</code> (Autoline, Europa‑Camiões, trucks.nl/Hexon, CustoJusto, Stockway…)</li>
<li>CSV: <code>{e(base_url)}/feeds/stock.csv</code></li>
<li>mobile.de (Seller API, enviado por script): <code>{e(base_url)}/feeds/mobile-de.json</code></li>
<li>Este relatório em JSON: <code>{e(base_url)}/feeds/relatorio.json</code></li></ul>
<h2>No feed ({len(rel['incluidos'])})</h2>{tbl(rel['incluidos'], ['id', 'ref', 'siteId', 'titulo', 'preco', 'estado', 'fotos'])}
<h2>À venda no artefacto mas sem fotos no site — não entram no feed ({len(rel['sem_fotos_no_site'])})</h2><p class="muted">Carregar o veículo no site (fotos + descrição) para passar a ser anunciado.</p>{tbl(rel['sem_fotos_no_site'], ['plate', 'stockNo', 'siteId', 'titulo', 'status'])}
<h2>No site mas sem registo no artefacto ({len(rel['sem_registo_no_artefacto'])})</h2><p class="muted">Acrescentar ao artefacto (ou ligar em dados/ligacoes.json) para serem anunciados; fica visível no site se ainda estiver no site antigo.</p>{tbl(rel['sem_registo_no_artefacto'], ['siteId', 'ref', 'titulo', 'noSiteAntigo'])}
<h2>Escondidos no site e nos feeds pelo estado do artefacto ({len(rel['ocultos_por_estado'])})</h2>{tbl(rel['ocultos_por_estado'], ['siteId', 'plate', 'status', 'dest', 'titulo'])}
<h2>Duplicados no site ({len(rel['duplicados_no_site'])})</h2>{tbl(rel['duplicados_no_site'], ['siteId', 'plate'])}
</body></html>'''
    with open(path_html, 'w', encoding='utf8') as f: f.write(body)

def generate(src, out_dir, base_url, stock=None, subtipos=None):
    """Gera os feeds em <out_dir>/feeds. Devolve (itens, relatório, ligação site->artefacto)."""
    stock = stock if stock is not None else load_json(os.path.join(src, 'stock.json'), [])
    subtipos = subtipos if subtipos is not None else load_json(os.path.join(src, 'subtipos.json'), {})
    estado = load_estado(src)
    ligacoes = (load_json(os.path.join(src, 'ligacoes.json'), {}) or {}).get('ligacoes', {})
    base_url = base_url.rstrip('/')
    items, rel = merged_items(stock, estado, ligacoes, subtipos, base_url)
    fd = os.path.join(out_dir, 'feeds'); os.makedirs(fd, exist_ok=True)
    gerado = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    write_xml(items, os.path.join(fd, 'stock.xml'), gerado)
    write_csv(items, os.path.join(fd, 'stock.csv'))
    write_mobile(items, os.path.join(fd, 'mobile-de.json'), gerado)
    write_report(rel, os.path.join(fd, 'relatorio.json'), os.path.join(fd, 'index.html'), gerado, base_url, estado)
    return items, rel, match_site_to_estado(stock, estado, ligacoes)

def feed_base_url():
    """URL onde este build vai ficar: SITE_URL (variável), senão o domínio *.pages.dev do deploy, senão ebtrucks.com."""
    u = os.environ.get('SITE_URL')
    if u: return u.rstrip('/')
    cf = os.environ.get('CF_PAGES_URL', '')
    m = re.match(r'https://[^.]+\.([^/]+\.pages\.dev)', cf)
    if m: return 'https://' + m.group(1)
    return SITE_CANONICO

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]
    base = sys.argv[3] if len(sys.argv) > 3 else feed_base_url()
    items, rel, _ = generate(src, out, base)
    print(f"feeds: {len(items)} viaturas em {os.path.join(out, 'feeds')} (base {base})")
    for k in ('sem_fotos_no_site', 'sem_registo_no_artefacto', 'ocultos_por_estado', 'duplicados_no_site'):
        print(f"  {k}: {len(rel[k])}")
