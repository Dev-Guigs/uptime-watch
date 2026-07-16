"""Sends incident/recovery notifications to Slack or Discord webhooks.

Tracks last-known state per service so it only notifies on state *transitions*
(up -> down, down -> up) rather than on every single check.
"""
from __future__ import annotations

import json
import urllib.request

from uptime_watch.checker import CheckResult


class StateChangeNotifier:
    def __init__(self, webhook_url: str | None = None, http_post=None) -> None:
        self.webhook_url = webhook_url
        self._http_post = http_post or _default_http_post
        self._last_state: dict[str, bool] = {}

    def process(self, result: CheckResult) -> str | None:
        """Update internal state and notify if this result represents a transition.

        Returns the notification message sent, or None if nothing was sent.
        """
        previous = self._last_state.get(result.service_name)
        self._last_state[result.service_name] = result.is_up

        if previous is None:
            return None  # first observation, nothing to compare against

        if previous == result.is_up:
            return None  # no state change

        if result.is_up:
            message = f":white_check_mark: *{result.service_name}* is back UP ({result.url})"
        else:
            message = (
                f":red_circle: *{result.service_name}* is DOWN ({result.url}) "
                f"— {result.error or 'unknown error'}"
            )

        if self.webhook_url:
            self._http_post(self.webhook_url, {"text": message})

        return message


def _default_http_post(url: str, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
        resp.read()
