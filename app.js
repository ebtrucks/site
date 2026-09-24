
/* ===================== CONFIGURAÇÃO ===================== */
const CFG = {
  // Fonte de dados. Nesta fase lê o stock real do site atual; na migração passa a "stock.json" no próprio site novo.

  waGeneral: '351932315888',   // botão flutuante (com indicativo 351)
  waSales:   '351912502690',   // botão "Enviar mensagem" na ficha
  newCount: 8,                 // quantos anúncios mais recentes levam a etiqueta NOVO
  siteUrl: 'https://ebtrucks.com'
};
/* ===================== TRADUÇÕES ===================== */
const T = {
 pt:{allmk:'Todas',allmk2:'as marcas',about:'Sobre nós',awards:'Prémios',topline:'Venda e exportação de veículos pesados · Mozelos, Portugal',fabout:'Mais de 20 anos a comprar e vender tratores, camiões e semi-reboques de todas as marcas.',kicker:'De Portugal para o mundo, sobre rodas',seeStock:'Ver stock',talk:'Falar no WhatsApp',export:'exportação mundial',w1t:'Veículos verificados',w1p:'Cada veículo é analisado em múltiplos pontos críticos para garantir qualidade e robustez.',w2t:'Todas as marcas',w2p:'Compramos e vendemos camiões, tratores e reboques de todas as marcas, a preço competitivo.',w3t:'Mais de 20 anos',w3p:'Mais de 5 000 veículos comprados e vendidos, em Portugal e no mercado internacional.',why:'Porquê a EB Trucks',sellT:'Tem veículos para venda?',sellP:'Compramos camiões, tratores e reboques. Envie-nos fotos e dados pelo WhatsApp.',sellB:'Propor veículo',sellMsg:'Olá! Tenho um veículo para vender. Envio fotos e dados.',awT:'Prémios e reconhecimento',awP:'Top 5% Melhores PME de Portugal e Melhor Empresa no Comércio de Veículos Automóveis (1000 PME, Exame 2022).',more:'Saber mais',rev:'O que dizem os clientes',photos:'fotos',stock:'Stock',contacts:'Contactos',address:'Morada',map:'Ver no mapa',follow:'Siga-nos',h1:'Tratores, camiões e semi-reboques usados',sub:'Venda e exportação para todo o mundo. Fale diretamente connosco por WhatsApp.',search:'Procurar marca, modelo ou referência…',go:'Procurar',sold:'veículos vendidos',years:'anos de experiência',instock:'em stock',all:'Todos',news:'Novidades',feat:'Destaques',vehicles:'veículos',brand:'Marca',any:'Qualquer',yfrom:'Ano desde',pmax:'Preço máx. €',sort:'Ordenar',s_new:'Mais recentes',s_old:'Mais antigos',s_pa:'Preço ↑',s_pd:'Preço ↓',s_ya:'Ano ↓',s_br:'Marca A–Z',clear:'Limpar',ask:'Preço sob consulta',isnew:'NOVO',star:'DESTAQUE',none:'Nenhum veículo encontrado com estes filtros.',back:'Voltar ao stock',ref:'Ref.',wa:'Enviar mensagem por WhatsApp',call:'Ligar',share:'Partilhar',copied:'Link copiado',year:'Ano',kms:'Quilómetros',fuel:'Combustível',gear:'Caixa',euro:'Norma Euro',axles:'Eixos',engine:'Cilindrada',hp:'Potência',reg:'Data de registo',cond:'Estado',color:'Cor',susp:'Suspensão',brakes:'Travões',beds:'Camas',tanks:'Depósitos',desc:'Descrição',specs:'Especificações',equip:'Equipamento',loading:'A carregar o stock…',err:'Não foi possível carregar o stock. Tente novamente dentro de momentos.',msg:(v)=>`Olá! Tenho interesse no ${v.title} (ref. ${v.ref}). Ainda está disponível?\n${v.url}`,hello:'Olá! Gostaria de mais informações sobre o vosso stock.'},
 en:{allmk:'All',allmk2:'makes',about:'About us',awards:'Awards',topline:'Sales and export of heavy vehicles · Mozelos, Portugal',fabout:'Over 20 years buying and selling tractor units, trucks and semi-trailers of all makes.',kicker:'From Portugal to the world, on wheels',seeStock:'View stock',talk:'Chat on WhatsApp',export:'worldwide export',w1t:'Inspected vehicles',w1p:'Every vehicle is checked at multiple critical points to ensure quality and robustness.',w2t:'All makes',w2p:'We buy and sell trucks, tractor units and trailers of all makes at competitive prices.',w3t:'Over 20 years',w3p:'More than 5,000 vehicles bought and sold, in Portugal and internationally.',why:'Why EB Trucks',sellT:'Do you have vehicles to sell?',sellP:'We buy trucks, tractor units and trailers. Send us photos and details on WhatsApp.',sellB:'Offer a vehicle',sellMsg:'Hello! I have a vehicle to sell. I will send photos and details.',awT:'Awards and recognition',awP:'Top 5% Best SMEs in Portugal and Best Company in Motor Vehicle Trade (1000 PME, Exame 2022).',more:'Learn more',rev:'What our customers say',photos:'photos',stock:'Stock',contacts:'Contacts',address:'Address',map:'View on map',follow:'Follow us',h1:'Used tractor units, trucks and semi-trailers',sub:'Sales and export worldwide. Talk to us directly on WhatsApp.',search:'Search make, model or reference…',go:'Search',sold:'vehicles sold',years:'years of experience',instock:'in stock',all:'All',news:'New arrivals',feat:'Featured',vehicles:'vehicles',brand:'Make',any:'Any',yfrom:'Year from',pmax:'Max price €',sort:'Sort',s_new:'Newest first',s_old:'Oldest first',s_pa:'Price ↑',s_pd:'Price ↓',s_ya:'Year ↓',s_br:'Make A–Z',clear:'Clear',ask:'Price on request',isnew:'NEW',star:'FEATURED',none:'No vehicles match these filters.',back:'Back to stock',ref:'Ref.',wa:'Send WhatsApp message',call:'Call',share:'Share',copied:'Link copied',year:'Year',kms:'Mileage',fuel:'Fuel',gear:'Gearbox',euro:'Euro standard',axles:'Axles',engine:'Engine capacity',hp:'Power',reg:'Registration date',cond:'Condition',color:'Colour',susp:'Suspension',brakes:'Brakes',beds:'Beds',tanks:'Fuel tanks',desc:'Description',specs:'Specifications',equip:'Equipment',loading:'Loading stock…',err:'Could not load the stock. Please try again shortly.',msg:(v)=>`Hello! I am interested in the ${v.title} (ref. ${v.ref}). Is it still available?\n${v.url}`,hello:'Hello! I would like more information about your stock.'},
 fr:{allmk:'Toutes',allmk2:'les marques',about:'À propos',awards:'Prix',topline:'Vente et export de véhicules lourds · Mozelos, Portugal',fabout:'Plus de 20 ans d’achat et de vente de tracteurs, camions et semi-remorques de toutes marques.',kicker:'Du Portugal vers le monde, sur roues',seeStock:'Voir le stock',talk:'Discuter sur WhatsApp',export:'export mondial',w1t:'Véhicules contrôlés',w1p:'Chaque véhicule est contrôlé sur de multiples points critiques pour garantir qualité et robustesse.',w2t:'Toutes marques',w2p:'Nous achetons et vendons camions, tracteurs et remorques de toutes marques à prix compétitif.',w3t:'Plus de 20 ans',w3p:'Plus de 5 000 véhicules achetés et vendus, au Portugal et à l’international.',why:'Pourquoi EB Trucks',sellT:'Vous avez des véhicules à vendre ?',sellP:'Nous achetons camions, tracteurs et remorques. Envoyez-nous photos et données par WhatsApp.',sellB:'Proposer un véhicule',sellMsg:'Bonjour ! J’ai un véhicule à vendre. J’envoie photos et données.',awT:'Prix et reconnaissance',awP:'Top 5 % des meilleures PME du Portugal et Meilleure entreprise du commerce de véhicules (1000 PME, Exame 2022).',more:'En savoir plus',rev:'Ce que disent nos clients',photos:'photos',stock:'Stock',contacts:'Contacts',address:'Adresse',map:'Voir sur la carte',follow:'Suivez-nous',h1:'Tracteurs, camions et semi-remorques d’occasion',sub:'Vente et export dans le monde entier. Contactez-nous directement sur WhatsApp.',search:'Rechercher marque, modèle ou référence…',go:'Rechercher',sold:'véhicules vendus',years:'ans d’expérience',instock:'en stock',all:'Tous',news:'Nouveautés',feat:'À la une',vehicles:'véhicules',brand:'Marque',any:'Toutes',yfrom:'Année depuis',pmax:'Prix max €',sort:'Trier',s_new:'Plus récents',s_old:'Plus anciens',s_pa:'Prix ↑',s_pd:'Prix ↓',s_ya:'Année ↓',s_br:'Marque A–Z',clear:'Effacer',ask:'Prix sur demande',isnew:'NOUVEAU',star:'À LA UNE',none:'Aucun véhicule ne correspond à ces filtres.',back:'Retour au stock',ref:'Réf.',wa:'Envoyer un message WhatsApp',call:'Appeler',share:'Partager',copied:'Lien copié',year:'Année',kms:'Kilométrage',fuel:'Carburant',gear:'Boîte',euro:'Norme Euro',axles:'Essieux',engine:'Cylindrée',hp:'Puissance',reg:'Date d’immatriculation',cond:'État',color:'Couleur',susp:'Suspension',brakes:'Freins',beds:'Couchettes',tanks:'Réservoirs',desc:'Description',specs:'Caractéristiques',equip:'Équipement',loading:'Chargement du stock…',err:'Impossible de charger le stock. Réessayez dans un instant.',msg:(v)=>`Bonjour ! Je suis intéressé par le ${v.title} (réf. ${v.ref}). Est-il toujours disponible ?\n${v.url}`,hello:'Bonjour ! Je souhaite plus d’informations sur votre stock.'},
 es:{allmk:'Todas',allmk2:'las marcas',about:'Sobre nosotros',awards:'Premios',topline:'Venta y exportación de vehículos pesados · Mozelos, Portugal',fabout:'Más de 20 años comprando y vendiendo tractoras, camiones y semirremolques de todas las marcas.',kicker:'De Portugal al mundo, sobre ruedas',seeStock:'Ver stock',talk:'Hablar por WhatsApp',export:'exportación mundial',w1t:'Vehículos verificados',w1p:'Cada vehículo se revisa en múltiples puntos críticos para garantizar calidad y robustez.',w2t:'Todas las marcas',w2p:'Compramos y vendemos camiones, tractoras y remolques de todas las marcas a precio competitivo.',w3t:'Más de 20 años',w3p:'Más de 5 000 vehículos comprados y vendidos, en Portugal y en el mercado internacional.',why:'Por qué EB Trucks',sellT:'¿Tiene vehículos en venta?',sellP:'Compramos camiones, tractoras y remolques. Envíenos fotos y datos por WhatsApp.',sellB:'Ofrecer vehículo',sellMsg:'¡Hola! Tengo un vehículo para vender. Envío fotos y datos.',awT:'Premios y reconocimiento',awP:'Top 5 % Mejores PYME de Portugal y Mejor Empresa en Comercio de Vehículos (1000 PME, Exame 2022).',more:'Saber más',rev:'Lo que dicen los clientes',photos:'fotos',stock:'Stock',contacts:'Contactos',address:'Dirección',map:'Ver en el mapa',follow:'Síguenos',h1:'Tractoras, camiones y semirremolques usados',sub:'Venta y exportación a todo el mundo. Hable directamente con nosotros por WhatsApp.',search:'Buscar marca, modelo o referencia…',go:'Buscar',sold:'vehículos vendidos',years:'años de experiencia',instock:'en stock',all:'Todos',news:'Novedades',feat:'Destacados',vehicles:'vehículos',brand:'Marca',any:'Cualquiera',yfrom:'Año desde',pmax:'Precio máx. €',sort:'Ordenar',s_new:'Más recientes',s_old:'Más antiguos',s_pa:'Precio ↑',s_pd:'Precio ↓',s_ya:'Año ↓',s_br:'Marca A–Z',clear:'Limpiar',ask:'Precio a consultar',isnew:'NUEVO',star:'DESTACADO',none:'Ningún vehículo coincide con estos filtros.',back:'Volver al stock',ref:'Ref.',wa:'Enviar mensaje por WhatsApp',call:'Llamar',share:'Compartir',copied:'Enlace copiado',year:'Año',kms:'Kilómetros',fuel:'Combustible',gear:'Caja',euro:'Norma Euro',axles:'Ejes',engine:'Cilindrada',hp:'Potencia',reg:'Fecha de matriculación',cond:'Estado',color:'Color',susp:'Suspensión',brakes:'Frenos',beds:'Camas',tanks:'Depósitos',desc:'Descripción',specs:'Especificaciones',equip:'Equipamiento',loading:'Cargando el stock…',err:'No se pudo cargar el stock. Inténtelo de nuevo en unos momentos.',msg:(v)=>`¡Hola! Me interesa el ${v.title} (ref. ${v.ref}). ¿Sigue disponible?\n${v.url}`,hello:'¡Hola! Me gustaría más información sobre su stock.'}
};
const EQUIP = {air_conditioning:['Ar condicionado','Air conditioning','Climatisation','Aire acondicionado'],parking_air_conditioning:['Ar condicionado de parque','Parking A/C','Clim. de stationnement','A/A de estacionamiento'],steering_wheel_adjustment:['Volante regulável','Adjustable steering wheel','Volant réglable','Volante regulable'],spare_tire:['Pneu suplente','Spare tyre','Roue de secours','Rueda de repuesto'],adjustable_seats:['Assentos reguláveis','Adjustable seats','Sièges réglables','Asientos regulables'],rotating_seats:['Bancos rotativos','Rotating seats','Sièges pivotants','Asientos giratorios'],tachometer:['Tacógrafo','Tachograph','Tachygraphe','Tacógrafo'],refrigerator:['Frigorífico','Fridge','Réfrigérateur','Nevera'],spoilers:['Spoilers','Spoilers','Spoilers','Spoilers'],pneumatic_seats:['Bancos pneumáticos','Air seats','Sièges pneumatiques','Asientos neumáticos'],sun_visor:['Pala de sol','Sun visor','Pare-soleil','Visera'],remote_control:['Comando à distância','Remote control','Télécommande','Mando a distancia'],gps:['GPS','GPS','GPS','GPS'],car_radio:['Auto-rádio','Radio','Autoradio','Radio'],tv:['TV','TV','TV','TV'],rear_view_cameras:['Câmaras traseiras','Rear cameras','Caméras de recul','Cámaras traseras'],central_locking:['Fecho centralizado','Central locking','Verrouillage centralisé','Cierre centralizado'],differential_lock:['Bloqueio do diferencial','Differential lock','Blocage de différentiel','Bloqueo de diferencial'],intarder:['Intarder','Intarder','Intarder','Intarder'],veb:['VEB','VEB','VEB','VEB'],abs:['ABS','ABS','ABS','ABS'],esp:['ESP','ESP','ESP','ESP'],tool:['Ferramenta','Tools','Outillage','Herramientas'],retarder:['Retarder','Retarder','Ralentisseur','Retarder'],crane:['Grua','Crane','Grue','Grúa'],adr:['ADR','ADR','ADR','ADR'],pto:['Tomada de força (PTO)','PTO','Prise de force','Toma de fuerza'],hydraulic_kit:['Kit hidráulico','Hydraulic kit','Kit hydraulique','Kit hidráulico'],platform:['Plataforma elevatória','Tail lift','Hayon élévateur','Plataforma elevadora'],cold_engine:['Motor de frio','Reefer unit','Groupe froid','Equipo de frío']};
const LI = {pt:0,en:1,fr:2,es:3};

/* ===================== ESTADO ===================== */
let lang = window.EB_LANG||'pt';
if(!T[lang]) lang='en';
const QS=new URLSearchParams(location.search);
const S = {all:[], loaded:false, error:false, f:{q:QS.get('q')||'',cat:+(QS.get('cat')||0),brand:'',yfrom:'',pmax:'',sort:'new'}, cache:{}};
const $ = (s,el=document)=>el.querySelector(s);
const t = k => T[lang][k];
const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = n => new Intl.NumberFormat(lang==='en'?'en-GB':'pt-PT').format(n);
const yearOf = v => { const d=v.characteristics&&v.characteristics.register_date; return d?+d.slice(0,4):null; };
const titleOf = v => `${(v.brand&&v.brand.name)||''} ${v.model||''}`.trim();
const priceHtml = v => v.price>0 ? `${fmt(v.price)} <small>EUR</small>` : null;
function descLines(html){ if(!html) return []; const d=new DOMParser().parseFromString(html,'text/html'); return [...d.body.querySelectorAll('p,li,div')].map(e=>e.textContent.trim()).filter(Boolean).filter((x,i,a)=>a.indexOf(x)===i) .concat(d.body.querySelector('p,li,div')?[]:[d.body.textContent.trim()].filter(Boolean)); }

/* ===================== DADOS ===================== */
const BASE = window.BASE||'';
function loadStock(){
  const out=(window.STOCK||[]).slice().sort((a,b)=>b.id-a.id);   // mais recente primeiro — sempre
  out.forEach(v=>{ v.image=v.photos&&v.photos[0]?{url:BASE+v.photos[0].replace(/^fotos\//,'thumbs/')}:null; });
  S.newIds=new Set(out.slice(0,CFG.newCount).map(v=>v.id));
  const nFeat=out.filter(v=>v.is_featured).length;
  S.featOk = nFeat>0 && nFeat<=Math.max(8,out.length/3);      // "destaque" só vale se for mesmo uma seleção
  S.all=out; S.loaded=true; S.error=!out.length;
  route();
}
async function loadOne(id){ const v=S.all.find(x=>x.id===id); if(!v) throw 0; return v; }

/* ===================== LISTA ===================== */
function filtered(){
  const f=S.f, q=f.q.trim().toLowerCase();
  let a=S.all.filter(v=>{
    if(f.cat && (!v.category||v.category.id!==f.cat)) return false;
    if(f.brand && (!v.brand||v.brand.name!==f.brand)) return false;
    if(f.yfrom && !((yearOf(v)||0)>=+f.yfrom)) return false;
    if(f.pmax && !(v.price>0 && v.price<=+f.pmax)) return false;
    if(q){ const hay=(titleOf(v)+' '+(v.ref||'')+' '+(v.category?v.category.name:'')+' '+descLines(v.description).join(' ')).toLowerCase(); if(!q.split(/\s+/).every(w=>hay.includes(w))) return false; }
    return true;
  });
  const by={new:(x,y)=>y.id-x.id, old:(x,y)=>x.id-y.id,
    pa:(x,y)=>(x.price||9e9)-(y.price||9e9), pd:(x,y)=>(y.price||0)-(x.price||0),
    ya:(x,y)=>(yearOf(y)||0)-(yearOf(x)||0), br:(x,y)=>titleOf(x).localeCompare(titleOf(y))};
  return a.sort(by[f.sort]||by.new);
}
function card(v){
  const y=yearOf(v), km=v.characteristics&&v.characteristics.kms, p=priceHtml(v), eu=v.motor_details&&v.motor_details.euro;
  const meta=[v.category&&v.category.name, y, km?fmt(km)+' km':null, eu?'Euro '+eu:null].filter(Boolean);
  return `<a class="card" href="${BASE}v/${v.slug}.html">
    <div class="ph">${v.image?`<img loading="lazy" decoding="async" src="${esc(v.image.url)}" alt="${esc(titleOf(v))}">`:''}
      ${S.newIds.has(v.id)?`<span class="tag">${t('isnew')}</span>`:''}${S.featOk&&v.is_featured?`<span class="tag star">★ ${t('star')}</span>`:''}
      ${v.photos&&v.photos.length>1?`<span class="n">${v.photos.length} ${t('photos')}</span>`:''}</div>
    <div class="cb"><div class="t">${esc(titleOf(v))}</div><div class="m">${meta.map(x=>`<i>${esc(x)}</i>`).join('')}</div>
      <div class="f"><div class="p ${p?'':'ask'}">${p||t('ask')}</div><span class="go">→</span></div></div></a>`;
}
function viewHome(){
  document.title='EB Trucks — '+t('h1');
  if(S.error) return $('#app').innerHTML=`<div class="wrap empty">${t('err')}</div>`;
  if(!S.loaded) return $('#app').innerHTML=`<div class="wrap empty">${t('loading')}</div>`;
  const cats=new Map(); S.all.forEach(v=>{ if(v.category){ const c=cats.get(v.category.id)||{id:v.category.id,name:v.category.name,n:0}; c.n++; cats.set(c.id,c);} });
  const brands=[...new Set(S.all.map(v=>v.brand&&v.brand.name).filter(Boolean))].sort();
  const f=S.f;
  const waSell=`https://wa.me/${CFG.waGeneral}?text=${encodeURIComponent(t('sellMsg'))}`;
  $('#app').innerHTML=`
  <section class="hero" style="background-image:url(${BASE}img/hero.jpg)"><div class="wrap">
    <span class="kicker">${t('kicker')}</span>
    <h1>${t('h1')}</h1><p>${t('sub')}</p>
    <form class="search" id="sf"><input id="q" type="search" placeholder="${t('search')}" value="${esc(f.q)}" aria-label="${t('go')}"><button class="btn">${t('go')}</button></form>
    <div class="cta"><a class="btn wa" href="https://wa.me/${CFG.waGeneral}?text=${encodeURIComponent(t('hello'))}" target="_blank" rel="noopener">${t('talk')}</a><a class="btn line" href="#stock">${t('seeStock')} ↓</a></div>
  </div></section>
  <div class="statbar"><div class="wrap"><div><b>${S.all.length}</b>${t('instock')}</div><div><b>+5 000</b>${t('sold')}</div><div><b>+20</b>${t('years')}</div><div><b>${t('allmk')}</b>${t('allmk2')}</div></div></div>
  <section class="sec" id="stock"><div class="wrap">
    <div class="cats" style="margin:0 0 28px"><button class="cat ${f.cat?'':'on'}" data-c="0">${t('all')}<span>${S.all.length}</span></button>
      ${[...cats.values()].sort((a,b)=>a.id-b.id).map(c=>`<button class="cat ${f.cat===c.id?'on':''}" data-c="${c.id}">${esc(c.name)}<span>${c.n}</span></button>`).join('')}</div>
    ${S.featOk?`<div class="sec-h"><h2>★ ${t('feat')}</h2></div><div class="grid" style="margin-bottom:36px">${S.all.filter(v=>v.is_featured).map(card).join('')}</div>`:''}
    <div class="sec-h"><h2>${t('news')}</h2><span class="count" id="cnt"></span></div>
    <div class="bar">
      <select id="fb" aria-label="${t('brand')}"><option value="">${t('brand')}: ${t('any')}</option>${brands.map(b=>`<option ${f.brand===b?'selected':''}>${esc(b)}</option>`).join('')}</select>
      <input id="fy" type="number" inputmode="numeric" placeholder="${t('yfrom')}" value="${esc(f.yfrom)}">
      <input id="fp" type="number" inputmode="numeric" placeholder="${t('pmax')}" value="${esc(f.pmax)}">
      <select id="fs" aria-label="${t('sort')}">${['new','old','pa','pd','ya','br'].map(k=>`<option value="${k}" ${f.sort===k?'selected':''}>${t('s_'+k)}</option>`).join('')}</select>
      <button class="btn ghost" id="fc">${t('clear')}</button></div>
    <div class="grid" id="grid"></div>
  </div></section>
  <section class="band"><div class="wrap"><div><h3>${t('sellT')}</h3><p>${t('sellP')}</p></div><a class="btn" href="${waSell}" target="_blank" rel="noopener">${t('sellB')}</a></div></section>
  <section class="sec alt"><div class="wrap"><div class="sec-h"><h2>${t('why')}</h2></div>
    <div class="why"><div><b>${t('w1t')}</b><p>${t('w1p')}</p></div><div><b>${t('w2t')}</b><p>${t('w2p')}</p></div><div><b>${t('w3t')}</b><p>${t('w3p')}</p></div></div></div></section>
  <section class="sec"><div class="wrap awards"><div><div class="sec-h"><h2>${t('awT')}</h2></div><p>${t('awP')}</p><a class="btn ghost" href="${BASE}premios.html">${t('more')}</a></div>
    <a href="${BASE}premios.html"><img loading="lazy" src="${BASE}img/premios.png" alt="${t('awT')}"></a></div></section>
  <section class="sec alt"><div class="wrap"><div class="sec-h"><h2>${t('rev')}</h2></div><div class="quotes">
    <div class="quote"><div class="s">★★★★★</div><p>“Grande conhecimento e seriedade em veículos pesados, tem sempre uma solução para cada cliente!!”</p><b>Fernando Gomes</b></div>
    <div class="quote"><div class="s">★★★★★</div><p>“Bom atendimento e bons negócios”</p><b>António Sousa</b></div></div></div></section>`;
  const draw=()=>{ const a=filtered(); $('#cnt').textContent=`${a.length} ${t('vehicles')}`; $('#grid').innerHTML=a.length?a.map(card).join(''):`<div class="empty" style="grid-column:1/-1">${t('none')}</div>`; };
  draw();
  $('#sf').onsubmit=e=>{e.preventDefault(); f.q=$('#q').value; draw(); $('#stock').scrollIntoView({block:'start'});};
  $('#q').oninput=e=>{f.q=e.target.value; draw();};
  $('#fb').onchange=e=>{f.brand=e.target.value; draw();};
  $('#fy').oninput=e=>{f.yfrom=e.target.value; draw();};
  $('#fp').oninput=e=>{f.pmax=e.target.value; draw();};
  $('#fs').onchange=e=>{f.sort=e.target.value; draw();};
  $('#fc').onclick=()=>{S.f={q:'',cat:0,brand:'',yfrom:'',pmax:'',sort:'new'}; viewHome();};
  document.querySelectorAll('.cat').forEach(b=>b.onclick=()=>{f.cat=+b.dataset.c; viewHome(); $('#stock').scrollIntoView({block:'start'});});
}

/* ===================== FICHA ===================== */
async function viewVehicle(id){
  $('#app').innerHTML=`<div class="wrap empty">${t('loading')}</div>`;
  let v; try{ v=await loadOne(id); }catch(e){ return $('#app').innerHTML=`<div class="wrap empty">${t('none')}<br><br><a class="btn" href="${BASE}index.html">${t('back')}</a></div>`; }
  const title=titleOf(v), y=yearOf(v), c=v.characteristics||{}, m=v.motor_details||{}, g=v.generic_details||{}, b=v.body_details||{};
  document.title=`${title} — EB Trucks`;
  const pics=(v.photos||[]).map(p=>({url:BASE+p,th:BASE+p.replace(/^fotos\//,'thumbs/')}));
  const url=`${CFG.siteUrl}/v/${v.slug}.html`;
  const wa=`https://wa.me/${CFG.waSales}?text=${encodeURIComponent(t('msg')({title,ref:v.ref||v.id,url}))}`;
  const p=priceHtml(v), li=LI[lang];
  const key=[[t('year'),y],[t('kms'),c.kms?fmt(c.kms)+' km':null],[t('gear'),m.gearbox_type],[t('euro'),m.euro?'Euro '+m.euro:null],[t('axles'),g.axles_configuration||g.axles_number||null],[t('fuel'),m.fuel]].filter(x=>x[1]);
  const rows=[[t('brand'),v.brand&&v.brand.name],[t('cond'),v.condition],[t('reg'),c.register_date?c.register_date.slice(0,10).split('-').reverse().join('/'):null],[t('engine'),m.engine_capacity?fmt(m.engine_capacity)+' cm³':null],[t('hp'),m.horse_power?m.horse_power+' cv':null],[t('tanks'),m.fuel_tanks_number],[t('susp'),(g.suspension||[]).join(', ')],[t('brakes'),g.brake_system],[t('beds'),b.bed_count],['Dimensões',b.body_dimensions&&typeof b.body_dimensions==='string'?b.body_dimensions:null]].filter(x=>x[1]);
  const equip=Object.entries({...g,...b}).filter(([k,val])=>val===true&&EQUIP[k]).map(([k])=>EQUIP[k][li]);
  const desc=descLines(v.description);
  $('#app').innerHTML=`<div class="wrap">
    <a class="back" href="${BASE}index.html">← ${t('back')}</a>
    <div class="det">
      <div><div class="gal"><div class="main"><img id="big" src="${pics[0]?esc(pics[0].url):''}" alt="${esc(title)}">
        ${pics.length>1?`<button class="nav l" id="pl" aria-label="prev">‹</button><button class="nav r" id="pr" aria-label="next">›</button><span class="cnt" id="pc"></span>`:''}</div>
        <div class="thumbs">${pics.map((x,i)=>`<img loading="lazy" data-i="${i}" src="${esc(x.th)}" alt="">`).join('')}</div></div>
        ${desc.length?`<div class="spec"><h3>${t('desc')}</h3>${desc.map(l=>`<div>${esc(l)}</div>`).join('')}</div>`:''}
        ${rows.length?`<div class="spec"><h3>${t('specs')}</h3><div class="rows">${rows.map(r=>`<div class="row"><span>${esc(r[0])}</span><b>${esc(r[1])}</b></div>`).join('')}</div></div>`:''}
        ${equip.length?`<div class="spec"><h3>${t('equip')}</h3><div class="chips">${equip.map(e=>`<i>✓ ${esc(e)}</i>`).join('')}</div></div>`:''}
      </div>
      <aside class="side"><h1>${esc(title)}</h1><div class="ref">${t('ref')} ${esc(v.ref||v.id)} · ${esc(v.category?v.category.name:'')}</div>
        <div class="price ${p?'':'ask'}" style="${p?'':'color:var(--red);font-size:22px'}">${p||t('ask')}</div>
        <div class="key">${key.map(k=>`<div><small>${esc(k[0])}</small><b>${esc(k[1])}</b></div>`).join('')}</div>
        <a class="btn wa" href="${wa}" target="_blank" rel="noopener">${t('wa')}</a>
        <a class="btn" href="tel:+351912502690">${t('call')} +351 912 502 690</a>
        <button class="btn ghost" id="sh">${t('share')}</button>
      </aside></div></div>`;
  let i=0; const show=n=>{ i=(n+pics.length)%pics.length; const big=$('#big'); big.onerror=()=>{big.onerror=null; big.src=pics[i].th;}; big.src=pics[i].url; if($('#pc')) $('#pc').textContent=`${i+1}/${pics.length}`; document.querySelectorAll('.thumbs img').forEach((e,k)=>e.classList.toggle('on',k===i)); };
  if(pics.length){ show(0); document.querySelectorAll('.thumbs img').forEach(e=>e.onclick=()=>show(+e.dataset.i)); if($('#pl')){ $('#pl').onclick=()=>show(i-1); $('#pr').onclick=()=>show(i+1);} }
  $('#sh').onclick=async()=>{ try{ if(navigator.share) await navigator.share({title,url}); else { await navigator.clipboard.writeText(url); $('#sh').textContent=t('copied'); } }catch(e){} };
  document.body.classList.add('veh');
  $('#app').insertAdjacentHTML('beforeend',`<div class="mcta"><a class="btn wa" href="${wa}" target="_blank" rel="noopener">WhatsApp</a><a class="btn" href="tel:+351912502690">${t('call')}</a></div>
    <div class="lb" id="lb"><button class="x" aria-label="close">×</button><button class="l" aria-label="prev">‹</button><img alt=""><button class="r" aria-label="next">›</button></div>`);
  const lb=$('#lb'), lbi=$('#lb img'); const lbShow=()=>{lbi.src=pics[i].url;};
  if(pics.length){ $('#big').onclick=()=>{lb.classList.add('on'); lbShow();}; $('#lb .x').onclick=()=>lb.classList.remove('on'); lb.onclick=e=>{if(e.target===lb) lb.classList.remove('on');};
    $('#lb .l').onclick=()=>{show(i-1); lbShow();}; $('#lb .r').onclick=()=>{show(i+1); lbShow();};
    document.onkeydown=e=>{ if(e.key==='Escape') lb.classList.remove('on'); if(e.key==='ArrowLeft'){show(i-1); if(lb.classList.contains('on')) lbShow();} if(e.key==='ArrowRight'){show(i+1); if(lb.classList.contains('on')) lbShow();} }; }
  window.scrollTo(0,0);
}

/* ===================== ROTAS / ARRANQUE ===================== */
function applyLang(){ document.documentElement.lang=lang; document.querySelectorAll('[data-i]').forEach(e=>e.textContent=t(e.dataset.i)); $('#lang').value=lang; $('#fab').href=`https://wa.me/${CFG.waGeneral}?text=${encodeURIComponent(t('hello'))}`; }
function route(){ if(window.PAGE) return; if(window.VID) viewVehicle(window.VID); else viewHome(); }
$('#lang').onchange=e=>{ try{localStorage.setItem('eb_lang',e.target.value)}catch(_){} const u=new URL(location.href); u.searchParams.set('lang',e.target.value); location.href=u.toString(); };
$('#yr').textContent=new Date().getFullYear();
$('#burger').onclick=()=>$('#nav').classList.toggle('open');
document.querySelectorAll('#nav a').forEach(a=>{ if(a.dataset.p===(window.PAGE||(window.VID?'':'home'))) a.classList.add('on'); a.addEventListener('click',()=>$('#nav').classList.remove('open')); });
applyLang(); loadStock();
