
/* ===================== CONFIGURAÇÃO ===================== */
const CFG = {
  // Fonte de dados. Nesta fase lê o stock real do site atual; na migração passa a "stock.json" no próprio site novo.

  waGeneral: '351932315888',   // botão flutuante (com indicativo 351)
  waSales:   '351912502690',   // botão "Enviar mensagem" na ficha
  newCount: 8,                 // quantos anúncios mais recentes levam a etiqueta NOVO
  siteUrl: 'https://ebtrucks.com'
};
/* ===================== TRADUÇÕES ===================== */
const T = window.I18N.ui; const EQUIP = window.I18N.equip; const SUB = window.I18N.sub; const SUBBY = window.I18N.subByCat;
const LI = Object.fromEntries(window.I18N.langs.map((l,i)=>[l,i]));
const fill=(str,v)=>String(str).replace(/\{(\w+)\}/g,(_,k)=>v[k]??'');
const PHONES=[['+351 912 502 690','+351912502690'],['+351 967 094 970','+351967094970'],['+351 227 442 388','+351227442388']];
const subName=k=>k&&SUB[k]?SUB[k][LI[lang]]||SUB[k][1]:'';

/* ===================== ESTADO ===================== */
let lang = window.EB_LANG||'pt';
if(!T[lang]) lang='en';
const isRTL=(window.I18N.rtl||[]).includes(lang);
const QS=new URLSearchParams(location.search);
const S = {all:[], loaded:false, error:false, f:{q:QS.get('q')||'',cat:+(QS.get('cat')||0),sub:QS.get('sub')||'',brand:'',yfrom:'',pmax:'',sort:'new'}, cache:{}};
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
    if(f.sub && v.sub_type!==f.sub) return false;
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
  const meta=[v.category&&v.category.name, v.sub_type?subName(v.sub_type):null, y, km?fmt(km)+' km':null, eu?'Euro '+eu:null].filter(Boolean);
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
      <select id="ft" aria-label="${t('type')}"><option value="0">${t('type')}: ${t('all')}</option>${[...cats.values()].sort((a,b)=>a.id-b.id).map(c=>`<option value="${c.id}" ${f.cat===c.id?'selected':''}>${esc(c.name)}</option>`).join('')}</select>
      ${f.cat&&SUBBY[f.cat]?`<select id="fsub" aria-label="${t('subtype')}"><option value="">${t('subtype')}: ${t('anySub')}</option>${SUBBY[f.cat].filter(k=>S.all.some(v=>v.sub_type===k&&v.category&&v.category.id===f.cat)).map(k=>`<option value="${k}" ${f.sub===k?'selected':''}>${esc(subName(k))}</option>`).join('')}</select>`:''}
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
  $('#ft').onchange=e=>{f.cat=+e.target.value; f.sub=''; viewHome();};
  if($('#fsub')) $('#fsub').onchange=e=>{f.sub=e.target.value; draw();};
  $('#fy').oninput=e=>{f.yfrom=e.target.value; draw();};
  $('#fp').oninput=e=>{f.pmax=e.target.value; draw();};
  $('#fs').onchange=e=>{f.sort=e.target.value; draw();};
  $('#fc').onclick=()=>{S.f={q:'',cat:0,sub:'',brand:'',yfrom:'',pmax:'',sort:'new'}; viewHome();};
  document.querySelectorAll('.cat').forEach(b=>b.onclick=()=>{f.cat=+b.dataset.c; f.sub=''; viewHome(); $('#stock').scrollIntoView({block:'start'});});
}

/* ===================== FICHA ===================== */
async function viewVehicle(id){
  $('#app').innerHTML=`<div class="wrap empty">${t('loading')}</div>`;
  let v; try{ v=await loadOne(id); }catch(e){ return $('#app').innerHTML=`<div class="wrap empty">${t('none')}<br><br><a class="btn" href="${BASE}index.html">${t('back')}</a></div>`; }
  const title=titleOf(v), y=yearOf(v), c=v.characteristics||{}, m=v.motor_details||{}, g=v.generic_details||{}, b=v.body_details||{};
  document.title=`${title} — EB Trucks`;
  const pics=(v.photos||[]).map(p=>({url:BASE+p,th:BASE+p.replace(/^fotos\//,'thumbs/')}));
  const url=`${CFG.siteUrl}/v/${v.slug}.html`;
  const wa=`https://wa.me/${CFG.waSales}?text=${encodeURIComponent(fill(t('msg'),{title,ref:v.ref||v.id,url}))}`;
  const p=priceHtml(v), li=LI[lang];
  const mailto=`mailto:info@ebtrucks.com?subject=${encodeURIComponent(fill(t('emailSubj'),{title,ref:v.ref||v.id}))}&body=${encodeURIComponent(fill(t('emailBody'),{title,ref:v.ref||v.id,url}))}`;
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
      <aside class="side"><h1>${esc(title)}</h1><div class="ref">${t('ref')} ${esc(v.ref||v.id)} · ${esc(v.category?v.category.name:'')}${v.sub_type?' · '+esc(subName(v.sub_type)):''}</div>
        <div class="price ${p?'':'ask'}" style="${p?'':'color:var(--red);font-size:22px'}">${p||t('ask')}</div>
        <div class="key">${key.map(k=>`<div><small>${esc(k[0])}</small><b>${esc(k[1])}</b></div>`).join('')}</div>
        <a class="btn wa" href="${wa}" target="_blank" rel="noopener">${t('wa')}</a>
        <div class="callwrap"><button class="btn" id="callbtn" type="button">☎ ${t('call3')}</button><div class="callmenu" id="callmenu">${PHONES.map(p=>`<a href="tel:${p[1]}">${p[0]}</a>`).join('')}</div></div>
        <a class="btn ghost" href="${mailto}">✉ ${t('email')}</a>
        <button class="btn ghost" id="sh">${t('share')}</button>
      </aside></div></div>`;
  let i=0; const show=n=>{ i=(n+pics.length)%pics.length; const big=$('#big'); big.onerror=()=>{big.onerror=null; big.src=pics[i].th;}; big.src=pics[i].url; if($('#pc')) $('#pc').textContent=`${i+1}/${pics.length}`; document.querySelectorAll('.thumbs img').forEach((e,k)=>e.classList.toggle('on',k===i)); };
  if(pics.length){ show(0); document.querySelectorAll('.thumbs img').forEach(e=>e.onclick=()=>show(+e.dataset.i)); if($('#pl')){ $('#pl').onclick=()=>show(i-1); $('#pr').onclick=()=>show(i+1);} }
  $('#sh').onclick=async()=>{ try{ if(navigator.share) await navigator.share({title,url}); else { await navigator.clipboard.writeText(url); $('#sh').textContent=t('copied'); } }catch(e){} };
  document.body.classList.add('veh');
  setTimeout(()=>{ const m=$('#callmenu'); const tg=e=>{e.preventDefault(); m.classList.toggle('on'); if(m.classList.contains('on')) m.scrollIntoView({block:'nearest'});}; $('#callbtn').onclick=tg; if($('#callbtn2')) $('#callbtn2').onclick=tg; document.addEventListener('click',e=>{ if(!e.target.closest('.callwrap,#callbtn2')) m.classList.remove('on'); }); },0);
  $('#app').insertAdjacentHTML('beforeend',`<div class="mcta"><a class="btn wa" href="${wa}" target="_blank" rel="noopener">WhatsApp</a><button class="btn" type="button" id="callbtn2">☎ ${t('call3')}</button><a class="btn ghost" href="${mailto}">✉</a></div>
    <div class="lb" id="lb"><button class="x" aria-label="close">×</button><button class="l" aria-label="prev">‹</button><img alt=""><button class="r" aria-label="next">›</button></div>`);
  const lb=$('#lb'), lbi=$('#lb img'); const lbShow=()=>{lbi.src=pics[i].url;};
  if(pics.length){ $('#big').onclick=()=>{lb.classList.add('on'); lbShow();}; $('#lb .x').onclick=()=>lb.classList.remove('on'); lb.onclick=e=>{if(e.target===lb) lb.classList.remove('on');};
    $('#lb .l').onclick=()=>{show(i-1); lbShow();}; $('#lb .r').onclick=()=>{show(i+1); lbShow();};
    document.onkeydown=e=>{ if(e.key==='Escape') lb.classList.remove('on'); if(e.key==='ArrowLeft'){show(i-1); if(lb.classList.contains('on')) lbShow();} if(e.key==='ArrowRight'){show(i+1); if(lb.classList.contains('on')) lbShow();} }; }
  window.scrollTo(0,0);
}

/* ===================== ROTAS / ARRANQUE ===================== */
function applyLang(){ document.documentElement.lang=lang; document.querySelectorAll('[data-i]').forEach(e=>e.textContent=t(e.dataset.i)); $('#lang').value=lang; $('#fab').href=`https://wa.me/${CFG.waGeneral}?text=${encodeURIComponent(t('hello'))}`; }
function viewContact(){
  const el=$('#contact-app'); if(!el) return;
  const veh=QS.get('veh')||'';
  el.innerHTML=`<div class="cgrid">
    <form class="cform" id="cf" novalidate>
      <p class="lead">${t('contactP')}</p>
      <label>${t('fName')} *<input name="name" required maxlength="120"></label>
      <label>${t('fEmail')} *<input name="email" type="email" required maxlength="160"></label>
      <label>${t('fPhone')}<input name="phone" maxlength="40"></label>
      <label>${t('fVeh')}<input name="vehicle" maxlength="160" value="${esc(veh)}"></label>
      <label>${t('fMsg')} *<textarea name="message" rows="6" required maxlength="4000"></textarea></label>
      <input name="website" class="hp" tabindex="-1" autocomplete="off">
      <button class="btn" type="submit">${t('fSend')}</button>
      <div class="fmsg" id="fmsg"></div>
    </form>
    <aside class="cinfo">
      <h3>${t('contacts')}</h3>
      ${PHONES.map(p=>`<div><a href="tel:${p[1]}">☎ ${p[0]}</a></div>`).join('')}
      <div><a href="mailto:info@ebtrucks.com">✉ info@ebtrucks.com</a></div>
      <div><a href="https://wa.me/${CFG.waGeneral}?text=${encodeURIComponent(t('hello'))}" target="_blank" rel="noopener">WhatsApp</a></div>
      <h3>${t('address')}</h3>
      <div><b>E.B., Lda.</b><br>EB Trucks<br>Rua Central da Vergada, 1550<br>4535-166 Mozelos<br>Santa Maria da Feira · Portugal</div>
      <div><a class="btn ghost" href="https://maps.app.goo.gl/Qb8imnmWAXvnyWox7" target="_blank" rel="noopener">${t('map')}</a></div>
    </aside></div>`;
  $('#cf').onsubmit=async e=>{ e.preventDefault(); const fd=new FormData(e.target); const d=Object.fromEntries(fd.entries()); const m=$('#fmsg');
    if(!d.name.trim()||!d.email.trim()||!d.message.trim()){ m.textContent=t('fReq'); m.className='fmsg err'; return; }
    m.textContent='…'; m.className='fmsg';
    try{ const r=await fetch(BASE+'api/contact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...d,lang})}); if(!r.ok) throw 0; m.textContent=t('fSent'); m.className='fmsg ok'; e.target.reset(); }
    catch(_){ const subj=encodeURIComponent((d.vehicle?d.vehicle+' — ':'')+d.name); const body=encodeURIComponent(d.message+'\n\n'+d.name+' · '+d.email+' · '+d.phone); m.innerHTML=t('fErr')+' <a href="mailto:info@ebtrucks.com?subject='+subj+'&body='+body+'">info@ebtrucks.com</a>'; m.className='fmsg err'; }
  };
}
function route(){ if(window.PAGE==='contactos') return viewContact(); if(window.PAGE) return; if(window.VID) viewVehicle(window.VID); else viewHome(); }
$('#lang').onchange=e=>{ try{localStorage.setItem('eb_lang',e.target.value)}catch(_){} const u=new URL(location.href); u.searchParams.set('lang',e.target.value); location.href=u.toString(); };
$('#yr').textContent=new Date().getFullYear();
$('#burger').onclick=()=>$('#nav').classList.toggle('open');
document.querySelectorAll('#nav a').forEach(a=>{ if(a.dataset.p===(window.PAGE||(window.VID?'':'home'))) a.classList.add('on'); a.addEventListener('click',()=>$('#nav').classList.remove('open')); });
applyLang(); loadStock();
