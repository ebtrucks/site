# Site EB Trucks

Gerador do site estático de ebtrucks.com.

- `dados/stock.json` — stock (55 veículos); `dados/fotos/{id}/` — fotos.
- `python3 build.py dados public maps.json` gera a pasta `public/` que a Cloudflare Pages publica.
