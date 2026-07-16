"""Command-line entry point for Uptime Watch."""
from __future__ import annotations

import argparse
import sys
import time

import yaml

from uptime_watch.checker import Service, check_all
from uptime_watch.notifier import StateChangeNotifier
from uptime_watch.status_page import render_status_page
from uptime_watch.storage import HistoryStore


def load_services(config_path: str) -> tuple[list[Service], dict]:
    raw = yaml.safe_load(open(config_path, encoding="utf-8")) or {}
    services = [Service(**s) for s in raw.get("services", [])]
    return services, raw.get("settings", {})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uptime-watch",
        description="Monitor HTTP service uptime, alert on state changes, "
        "and generate a static status page.",
    )
    parser.add_argument("-c", "--config", required=True, help="Path to YAML config file")
    parser.add_argument("--db", default="uptime.db", help="Path to SQLite history DB")
    parser.add_argument("--status-page", default="status.html", help="Output HTML path")
    parser.add_argument("--once", action="store_true", help="Run a single check pass and exit")
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    services, settings = load_services(args.config)

    if not services:
        print("No services configured. Nothing to check.", file=sys.stderr)
        return 1

    store = HistoryStore(args.db)
    notifier = StateChangeNotifier(webhook_url=settings.get("webhook_url"))
    interval = float(settings.get("interval_seconds", 30))

    def check_pass() -> None:
        results = check_all(services)
        store.record_all(results)
        for result in results:
            status = "UP  " if result.is_up else "DOWN"
            print(f"[{status}] {result.service_name:<20} {result.url}")
            message = notifier.process(result)
            if message:
                print(f"  -> notified: {message}")

        stats = [store.uptime_stats(s.name) for s in services]
        render_status_page(stats, args.status_page)

    check_pass()
    if not args.once:
        while True:
            time.sleep(interval)
            check_pass()

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
