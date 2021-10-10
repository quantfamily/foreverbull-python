from foreverbull_core import broker
from foreverbull.input_parser import InputParser
import socket

def test_input_parser():
    file_name = "file.py"
    broker_url = "broker_url"
    local_host = "local_host"
    executors = "10"
    service_id = "service-id"
    instance_id = "instance-id"
    args = [file_name, "--broker-url", broker_url, "--local-host", local_host, "--executors", executors,
    "--service-id", service_id, "--instance-id", instance_id]
    ip = InputParser()
    parsed = ip.parse_input(args)
    assert file_name == parsed.file
    assert broker_url == parsed.broker_url
    assert local_host == parsed.local_host
    assert executors == parsed.executors
    assert service_id == parsed.service_id
    assert instance_id == parsed.instance_id

def test_input_defaults():
    file_name = "file.py"
    service_id = "service-id"
    instance_id = "instance-id"
    ip = InputParser()
    args = [file_name, "--service-id", service_id, "--instance-id", instance_id]
    parsed = ip.parse_input(args)

    assert file_name == parsed.file
    assert "127.0.0.1:8080" == parsed.broker_url
    assert socket.gethostbyname(socket.gethostname()) == parsed.local_host
    assert 1 == parsed.executors
    assert service_id == parsed.service_id
    assert instance_id == parsed.instance_id