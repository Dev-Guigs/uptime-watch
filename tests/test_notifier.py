from uptime_watch.checker import CheckResult
from uptime_watch.notifier import StateChangeNotifier


def make_result(is_up):
    return CheckResult(
        service_name="api",
        url="https://api.example.com",
        is_up=is_up,
        status_code=200 if is_up else 500,
        response_time_ms=10.0,
        error=None if is_up else "server error",
        checked_at=0.0,
    )


def test_first_observation_does_not_notify():
    sent = []
    notifier = StateChangeNotifier(
        webhook_url="https://hooks.example.com/x",
        http_post=lambda url, payload: sent.append(payload),
    )
    message = notifier.process(make_result(is_up=True))

    assert message is None
    assert sent == []


def test_transition_to_down_notifies():
    sent = []
    notifier = StateChangeNotifier(
        webhook_url="https://hooks.example.com/x",
        http_post=lambda url, payload: sent.append(payload),
    )
    notifier.process(make_result(is_up=True))
    message = notifier.process(make_result(is_up=False))

    assert message is not None
    assert "DOWN" in message
    assert len(sent) == 1


def test_no_change_does_not_notify_again():
    sent = []
    notifier = StateChangeNotifier(
        webhook_url="https://hooks.example.com/x",
        http_post=lambda url, payload: sent.append(payload),
    )
    notifier.process(make_result(is_up=True))
    notifier.process(make_result(is_up=True))
    notifier.process(make_result(is_up=True))

    assert sent == []


def test_recovery_notifies_up_message():
    sent = []
    notifier = StateChangeNotifier(
        webhook_url="https://hooks.example.com/x",
        http_post=lambda url, payload: sent.append(payload),
    )
    notifier.process(make_result(is_up=True))
    notifier.process(make_result(is_up=False))
    message = notifier.process(make_result(is_up=True))

    assert message is not None
    assert "UP" in message
