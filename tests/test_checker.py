import requests

from uptime_watch.checker import Service, check_all, check_service


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


def fake_get_ok(url, timeout):
    return FakeResponse(200)


def fake_get_wrong_status(url, timeout):
    return FakeResponse(503)


def fake_get_raises(url, timeout):
    raise requests.exceptions.ConnectionError("connection refused")


def test_check_service_up():
    service = Service(name="api", url="https://api.example.com/health")
    result = check_service(service, http_get=fake_get_ok)

    assert result.is_up is True
    assert result.status_code == 200
    assert result.error is None
    assert result.response_time_ms is not None


def test_check_service_wrong_status_is_down():
    service = Service(name="api", url="https://api.example.com/health")
    result = check_service(service, http_get=fake_get_wrong_status)

    assert result.is_up is False
    assert result.status_code == 503
    assert "503" in result.error


def test_check_service_connection_error_is_down():
    service = Service(name="api", url="https://api.example.com/health")
    result = check_service(service, http_get=fake_get_raises)

    assert result.is_up is False
    assert result.status_code is None
    assert "connection refused" in result.error


def test_check_all_runs_every_service():
    services = [
        Service(name="a", url="https://a.example.com"),
        Service(name="b", url="https://b.example.com"),
    ]
    results = check_all(services, http_get=fake_get_ok)

    assert len(results) == 2
    assert all(r.is_up for r in results)
