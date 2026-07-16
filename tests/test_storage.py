from uptime_watch.checker import CheckResult
from uptime_watch.storage import HistoryStore


def make_result(is_up=True, response_time_ms=50.0, checked_at=1000.0):
    return CheckResult(
        service_name="api",
        url="https://api.example.com",
        is_up=is_up,
        status_code=200 if is_up else 503,
        response_time_ms=response_time_ms,
        error=None if is_up else "unexpected status 503",
        checked_at=checked_at,
    )


def test_record_and_uptime_stats_all_up():
    store = HistoryStore(":memory:")
    for i in range(5):
        store.record(make_result(is_up=True, checked_at=1000.0 + i))

    stats = store.uptime_stats("api")
    assert stats.total_checks == 5
    assert stats.up_checks == 5
    assert stats.uptime_percent == 100.0
    assert stats.last_status is True


def test_uptime_stats_mixed_results():
    store = HistoryStore(":memory:")
    store.record(make_result(is_up=True, checked_at=1000.0))
    store.record(make_result(is_up=False, checked_at=1001.0))
    store.record(make_result(is_up=True, checked_at=1002.0))
    store.record(make_result(is_up=False, checked_at=1003.0))

    stats = store.uptime_stats("api")
    assert stats.total_checks == 4
    assert stats.up_checks == 2
    assert stats.uptime_percent == 50.0
    assert stats.last_status is False


def test_uptime_stats_no_data_returns_zero():
    store = HistoryStore(":memory:")
    stats = store.uptime_stats("nonexistent")
    assert stats.total_checks == 0
    assert stats.uptime_percent == 0.0
    assert stats.last_status is None


def test_recent_incidents_only_returns_downs():
    store = HistoryStore(":memory:")
    store.record(make_result(is_up=True, checked_at=1000.0))
    store.record(make_result(is_up=False, checked_at=1001.0))
    store.record(make_result(is_up=False, checked_at=1002.0))

    incidents = store.recent_incidents("api")
    assert len(incidents) == 2
    # Most recent first
    assert incidents[0]["checked_at"] == 1002.0
