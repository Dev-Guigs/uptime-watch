# 🟢 Uptime Watch

[![CI](https://github.com/Dev-Guigs/uptime-watch/actions/workflows/ci.yml/badge.svg)](https://github.com/Dev-Guigs/uptime-watch/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Um monitor de **uptime self-hosted** e enxuto: verifica uma lista de
serviços HTTP em intervalos, guarda o histórico em SQLite, notifica
Slack/Discord apenas em *transições* de estado (não em toda checagem) e
gera uma status page estática — seu próprio mini clone do "status.io" em
um único processo Python.

## Por que este projeto existe

Monitoramento de uptime é uma das primeiras coisas que uma vaga de
DevOps/SRE toca. Este projeto mantém as peças propositalmente simples e
fáceis de inspecionar: SQLite em vez de um banco completo, um arquivo HTML
estático em vez de um framework web — mas a lógica de domínio (alertas
baseados em transição de estado, cálculo de % de uptime) é exatamente o
que ferramentas de produção fazem.

## Arquitetura

```
┌──────────┐   HTTP GET   ┌─────────┐  transição?  ┌──────────────────┐
│ Serviços │─────────────►│ Checker │─────────────►│ StateChangeNotify │──► Slack/Discord
└──────────┘              └────┬────┘               └──────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │ HistoryStore  │ (SQLite)
                        └───────┬───────┘
                                ▼
                        ┌───────────────┐
                        │ status.html   │ (Jinja2)
                        └───────────────┘
```

## Funcionalidades

- 🔁 Verifica qualquer número de endpoints HTTP em intervalo configurável
- 📉 Acompanha % de uptime, tempo médio de resposta e histórico de incidentes em SQLite
- 🔔 Alertas via webhook Slack/Discord **apenas em mudança de estado** (up→down, down→up)
- 📄 Gera uma `status.html` estática e estilizada, que você pode servir em qualquer lugar
- ✅ Totalmente testado, com transporte HTTP e de notificação injetáveis
- ⚡ Modo `--once` para cron jobs / smoke tests em CI

## Instalação

```bash
git clone https://github.com/Dev-Guigs/uptime-watch.git
cd uptime-watch
pip install -r requirements.txt
```

## Uso

1. Copie e edite a configuração de exemplo:

   ```bash
   cp examples/config.example.yml config.yml
   ```

   ```yaml
   services:
     - name: API Principal
       url: https://api.example.com/health
       expected_status: 200
       timeout_seconds: 5

   settings:
     interval_seconds: 30
     webhook_url: https://hooks.slack.com/services/xxx
   ```

2. Execute:

   ```bash
   python -m uptime_watch.cli --config config.yml --db uptime.db --status-page status.html
   ```

3. Abra `status.html` no navegador — ela é atualizada a cada rodada de checagem.

### Modo one-shot (para cron / CI)

```bash
python -m uptime_watch.cli --config config.yml --once
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest --cov=uptime_watch
```

## Roadmap

- [ ] Servir `status.html` por um pequeno servidor HTTP embutido
- [ ] Gráfico histórico de uptime (últimas 24h/7d/30d)
- [ ] Checagens multi-região (rodar de vários hosts, agregar resultados)

## Licença

MIT — veja [LICENSE](LICENSE).
