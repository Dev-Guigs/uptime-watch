# 🟢 Uptime Watch

[![CI](https://github.com/OWNER/uptime-watch/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/uptime-watch/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A small, self-hosted **uptime monitor**: checks a list of HTTP services on an
interval, stores history in SQLite, notifies Slack/Discord only on state
*transitions* (not every check), and renders a static status page — your
own mini "status.io" clone in one Python process.

## Why this exists

Uptime monitoring is one of the first things a DevOps/SRE role touches.
This project intentionally keeps the moving parts simple and inspectable:
SQLite instead of a full database, a static HTML file instead of a web
framework, but the domain logic (transition-based alerting, uptime %
calculation) is exactly what production tools do.

## Architecture

```
┌──────────┐   HTTP GET   ┌─────────┐  transition?  ┌──────────────────┐
│ Services │─────────────►│ Checker │──────────────►│ StateChangeNotify │──► Slack/Discord
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

## Features

- 🔁 Polls any number of HTTP endpoints on a configurable interval
- 📉 Tracks uptime %, average response time, and incident history in SQLite
- 🔔 Slack/Discord webhook alerts **only on state change** (up→down, down→up)
- 📄 Generates a static, styled `status.html` you can serve anywhere
- ✅ Fully unit tested with injectable HTTP + notification transports
- ⚡ `--once` mode for cron jobs / CI smoke tests

## Installation

```bash
git clone https://github.com/OWNER/uptime-watch.git
cd uptime-watch
pip install -r requirements.txt
```

## Usage

1. Copy and edit the example config:

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

2. Run it:

   ```bash
   python -m uptime_watch.cli --config config.yml --db uptime.db --status-page status.html
   ```

3. Open `status.html` in a browser — it updates after every check pass.

### One-shot mode (for cron / CI)

```bash
python -m uptime_watch.cli --config config.yml --once
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest --cov=uptime_watch
```

## Roadmap

- [ ] Serve `status.html` over a tiny built-in HTTP server
- [ ] Historical uptime chart (last 24h/7d/30d)
- [ ] Multi-region checks (run from several hosts, aggregate results)

## License

MIT — see [LICENSE](LICENSE).
