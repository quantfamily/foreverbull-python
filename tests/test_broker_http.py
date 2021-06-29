import requests_mock
import requests
from foreverbull.broker.http import RequestError
from foreverbull.broker.http.backtest import Backtest
from foreverbull.broker.http.service import Service
import pytest


@pytest.fixture(scope="function")
def backtest_session():
    def setup():
        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount("http://", adapter)
        backtest = Backtest("127.0.0.1", session=session)
        return backtest, adapter

    return setup


@pytest.fixture(scope="function")
def service_session():
    def setup():
        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount("http://", adapter)
        service = Service("127.0.0.1", session=session)
        return service, adapter

    return setup


def test_list_backtests(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/backtests", json=[])
    rsp = backtest.list_backtests()
    assert rsp == []


def test_list_backtests_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/backtests", json=[], status_code=500)
    with pytest.raises(RequestError, match="get call /backtests gave bad return code: 500"):
        backtest.list_backtests()


def test_create_backtest(backtest_session):
    backtest, adapter = backtest_session()
    config = {
        "start_date": "2020-01-01",
        "end_date": "2022-12-31",
        "timezone": "utc",
        "benchmark": "AAPL",
        "assets": ["AAPLE", "TSLA"],
    }
    created_backtest = {"id": 1, "config": config}
    adapter.register_uri("POST", "http://127.0.0.1:8080/backtests", json=created_backtest)
    rsp = backtest.create_backtest(config)
    assert rsp["id"] == created_backtest["id"]


def test_create_backtest_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/backtests", json={}, status_code=500)
    with pytest.raises(RequestError, match="post call /backtests gave bad return code: 500"):
        backtest.create_backtest({})


def test_get_backtest(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/backtests/1", json={})
    backtest.get_backtest(1)


def test_get_backtest_negative(backtest_session):
    backtest, adapter = backtest_session()
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/backtests/1", status_code=500)
    with pytest.raises(RequestError, match="get call /backtests/1 gave bad return code: 500"):
        backtest.get_backtest(1)


def test_delete_backtest(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/backtests/1")
    backtest.delete_backtest(1)


def test_delete_backtest_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/backtests/1", status_code=500)
    with pytest.raises(RequestError, match="delete call /backtests/1 gave bad return code: 500"):
        backtest.delete_backtest(1)


def test_list_backtest_services(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/backtests/1/services", json=[])
    rsp = backtest.list_backtest_services(1)
    assert rsp == []


def test_list_backtest_services_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/backtests/1/services", status_code=500)
    with pytest.raises(RequestError, match="get call /backtests/1/services gave bad return code: 500"):
        backtest.list_backtest_services(1)


def test_add_backtest_services(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("PUT", "http://127.0.0.1:8080/backtests/1/service")
    backtest.add_backtest_service(1, {})


def test_add_backtest_services_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("PUT", "http://127.0.0.1:8080/backtests/1/service", status_code=500)
    with pytest.raises(RequestError, match="post call /backtests/1/services gave bad return code: 500"):
        backtest.add_backtest_service(1, {})


def test_list_sessions(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/backtests/1/sessions", json=[])
    assert backtest.list_sessions(1) == []


def test_list_sessions_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/backtests/1/sessions", status_code=500)
    with pytest.raises(RequestError, match="get call /backtests/1/sessions gave bad return code: 500"):
        backtest.list_sessions(1)


def test_create_session(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/backtests/1/sessions", json={})
    assert backtest.create_session(1) == {}


def test_create_session_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/backtests/1/sessions", status_code=500)
    with pytest.raises(RequestError, match="post call /backtests/1/sessions gave bad return code: 500"):
        backtest.create_session(1)


def test_get_session(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/backtests/1/sessions/1", json={})
    assert backtest.get_session(1, 1) == {}


def test_get_session_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/backtests/1/sessions/1", status_code=500)
    with pytest.raises(RequestError, match="get call /backtests/1/sessions/1 gave bad return code: 500"):
        backtest.get_session(1, 1)


def test_delete_session(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/backtests/1/sessions/1")
    assert backtest.delete_session(1, 1) is True


def test_delete_session_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/backtests/1/sessions/1", status_code=500)
    with pytest.raises(RequestError, match="delete call /backtests/1/sessions/1 gave bad return code: 500"):
        backtest.delete_session(1, 1)


def test_run_session(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/backtests/1/sessions/1/run", json={})
    assert backtest.run_session(1, 1, {}) == {}


def test_run_session_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/backtests/1/sessions/1/run", status_code=500)
    with pytest.raises(RequestError, match="post call /backtests/1/sessions/1/run gave bad return code: 500"):
        backtest.run_session(1, 1, {})


def test_list_services(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services", json=[])
    assert service.list_services() == []


def test_list_services_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services", status_code=500)

    with pytest.raises(RequestError, match="get call /services gave bad return code: 500"):
        service.list_services()


def test_create_service(service_session):
    service, adapter = service_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/services", json={"id": 1})
    assert service.create_service({}) == {"id": 1}


def test_create_service_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/services", status_code=500)

    with pytest.raises(RequestError, match="post call /services gave bad return code: 500"):
        service.create_service({})


def test_get_service(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services/1", json={"id": 1})
    assert service.get_service(1) == {"id": 1}


def test_get_service_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services/1", status_code=500)

    with pytest.raises(RequestError, match="get call /services/1 gave bad return code: 500"):
        service.get_service(1)


def test_delete_service(service_session):
    service, adapter = service_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/services/1")
    assert service.delete_service(1) is True


def test_delete_service_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/services/1", status_code=500)

    with pytest.raises(RequestError, match="delete call /services/1 gave bad return code: 500"):
        service.delete_service(1)


def test_list_instances(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services/1/instances", json=[])
    assert service.list_instances(1) == []


def test_list_instances_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services/1/instances", status_code=500)

    with pytest.raises(RequestError, match="get call /services/1/instances gave bad return code: 500"):
        service.list_instances(1)


def test_create_instance(service_session):
    service, adapter = service_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/services/1/instances", json={"id": 14})
    assert service.create_instance(1, {}) == {"id": 14}


def test_create_instance_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/services/1/instances", status_code=500)

    with pytest.raises(RequestError, match="post call /services/1/instances gave bad return code: 500"):
        service.create_instance(1, {})


def test_get_instance(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services/1/instances/1", json={"id": 14})
    assert service.get_instance(1, 1) == {"id": 14}


def test_get_instance_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services/1/instances/1", status_code=500)

    with pytest.raises(RequestError, match="get call /services/1/instances/1 gave bad return code: 500"):
        service.get_instance(1, 1)


def test_delete_instance(service_session):
    service, adapter = service_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/services/1/instances/1")
    assert service.delete_instance(1, 1) is True


def test_delete_instance_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/services/1/instances/1", status_code=500)

    with pytest.raises(RequestError, match="delete call /services/1/instances/1 gave bad return code: 500"):
        service.delete_instance(1, 1)


def test_list_containers(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services/containers", json=[])
    assert service.list_containers() == []


def test_list_containers_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services/containers", status_code=500)

    with pytest.raises(RequestError, match="get call /services/containers gave bad return code: 500"):
        service.list_containers()


def test_create_container(service_session):
    service, adapter = service_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/services/containers", json={})
    assert service.create_container({}) == {}


def test_create_container_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/services/containers", status_code=500)

    with pytest.raises(RequestError, match="post call /services/containers gave bad return code: 500"):
        service.create_container({})


def test_get_container(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services/containers/1", json={})
    assert service.get_container(1) == {}


def test_get_container_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/services/containers/1", status_code=500)

    with pytest.raises(RequestError, match="get call /services/containers/1 gave bad return code: 500"):
        service.get_container(1)


def test_delete_container(service_session):
    service, adapter = service_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/services/containers/1", json={})
    assert service.delete_container(1) is True


def test_delete_container_negative(service_session):
    service, adapter = service_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/services/containers/1", status_code=500)

    with pytest.raises(RequestError, match="delete call /services/containers/1 gave bad return code: 500"):
        service.delete_container(1)


def test_HTTPClient():
    pass
