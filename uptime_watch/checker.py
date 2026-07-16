"""HTTP health checking for a set of monitored services."""
from __future__ import annotations

import time
from dataclasses import dataclass

import requests


@dataclass
class Service:
    name: str
    url: str
    expected_status: int = 200
    timeout_seconds: float = 5.0


@dataclass
class CheckResult:
    service_name: str
    url: str
    is_up: bool
    status_code: int | None
    response_time_ms: float | None
    error: str | None
    checked_at: float


def check_service(service: Service, http_get=None) -> CheckResult:
    """Perform a single HTTP check against a service.

    `http_get` is injectable so tests never touch the network.
    """
    http_get = http_get or requests.get
    started = time.time()
    try:
        response = http_get(service.url, timeout=service.timeout_seconds)
        elapsed_ms = (time.time() - started) * 1000
        is_up = response.status_code == service.expected_status
        return CheckResult(
            service_name=service.name,
            url=service.url,
            is_up=is_up,
            status_code=response.status_code,
            response_time_ms=round(elapsed_ms, 2),
            error=None if is_up else f"unexpected status {response.status_code}",
            checked_at=started,
        )
    except requests.RequestException as exc:
        return CheckResult(
            service_name=service.name,
            url=service.url,
            is_up=False,
            status_code=None,
            response_time_ms=None,
            error=str(exc),
            checked_at=started,
        )


def check_all(services: list[Service], http_get=None) -> list[CheckResult]:
    return [check_service(service, http_get=http_get) for service in services]
