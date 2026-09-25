// Formulário de contactos → email para info@ebtrucks.com (Resend). Sem RESEND_API_KEY devolve 503 e o site recorre ao mailto.
export async function onRequestPost({ request, env }) {
  let d; try { d = await request.json(); } catch { return new Response('bad json', { status: 400 }); }
  const s = (x, n) => String(x || '').slice(0, n).trim();
  const name = s(d.name, 120), email = s(d.email, 160), phone = s(d.phone, 40), vehicle = s(d.vehicle, 160), message = s(d.message, 4000), lang = s(d.lang, 5);
  if (d.website) return new Response('ok', { status: 200 });               // honeypot (bots)
  if (!name || !email || !message || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return new Response('invalid', { status: 422 });
  if (!env.RESEND_API_KEY) return new Response('mail not configured', { status: 503 });
  const to = env.CONTACT_TO || 'info@ebtrucks.com';
  const from = env.CONTACT_FROM || 'EB Trucks <site@ebtrucks.com>';
  const text = `Nome: ${name}\nEmail: ${email}\nTelefone/WhatsApp: ${phone || '-'}\nVeículo: ${vehicle || '-'}\nLíngua: ${lang}\n\n${message}\n`;
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST', headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from, to: [to], reply_to: email, subject: `[Site] ${vehicle ? vehicle + ' — ' : ''}${name}`, text })
  });
  if (!r.ok) return new Response('send failed', { status: 502 });
  return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'Content-Type': 'application/json' } });
}
