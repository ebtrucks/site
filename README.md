# Site EB Trucks

Gerador do site estático de ebtrucks.com e dos feeds para os portais.

- `dados/stock.json` — catálogo (conteúdo dos anúncios: título, descrição, preço de tabela, fotos); `dados/fotos/{id}/` — fotos.
- `dados/estado.json` — instantâneo do artefacto «Ebtrucks Stock» (claude.ai): estado de cada viatura, preço, km. **É o artefacto que decide o que está à venda.**
- `dados/ligacoes.json` — ligações forçadas id do site ↔ matrícula, quando a `ref` do site não chega.
- `python3 build.py dados public maps.json` gera a pasta `public/` que a Cloudflare Pages publica — site + `public/feeds/`.

## Feeds para os portais (`/feeds/`)
Gerados em cada build a partir de stock.json + estado.json (só viaturas Disponível/Reservado, com fotos):
- `feeds/stock.xml` e `feeds/stock.csv` — feed genérico (Autoline, Europa‑Camiões, trucks.nl/Hexon, CustoJusto, Stockway…).
- `feeds/mobile-de.json` — anúncios no formato da Seller API do mobile.de; `tools/mobile_de_push.py` envia-os (GitHub Actions `mobile-de.yml`, precisa dos segredos `MOBILE_DE_USER`/`MOBILE_DE_PASSWORD`).
- `feeds/index.html` e `feeds/relatorio.json` — o que entrou e o que ficou de fora (sem fotos no site, sem registo no artefacto…).
- `python3 feeds.py dados public` gera só os feeds, sem o site.

## Ferramentas
- `tools/importar_site_antigo.py` — enquanto o site antigo (Laravel) for onde se carregam fotos, traz de lá os veículos novos e atualiza os existentes (não apaga: marca `no_site_antigo: false`).
- Tarefa agendada no Claude «Portais — sincronizar stock»: lê o artefacto → escreve `dados/estado.json` → corre o importador → faz push → a Cloudflare reconstrói o site e os feeds.
