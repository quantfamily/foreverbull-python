from foreverbull.broker.broker import Broker
from foreverbull.broker.models import Base, Database, Initialization


def test_base_model():
    assert "required" not in Base.schema()


def test_database_model():
    required_fields = ["user", "password", "hostname", "port", "db_name", "dialect"]
    assert Database.schema()["required"] == required_fields


def test_initialization_model():
    assert Initialization.schema()["required"] == ["session_id"]


def test_broker():
    b = Broker("127.0.0.1")
    local_connection = b.local_connection()
    assert "host" in local_connection
    assert local_connection["host"] == "127.0.0.1"
    assert "port" in local_connection
    assert local_connection["port"] > 1000
    assert "online" in local_connection
    assert local_connection["online"] is True
    assert "listen" in local_connection
    assert local_connection["listen"] is True
