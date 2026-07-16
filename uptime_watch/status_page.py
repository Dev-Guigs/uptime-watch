"""Generates a static status-page HTML file from current uptime stats."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from uptime_watch.storage import UptimeStats

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_status_page(stats: list[UptimeStats], output_path: str) -> None:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("status.html")
    html = template.render(stats=stats)
    Path(output_path).write_text(html, encoding="utf-8")
