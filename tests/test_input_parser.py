from foreverbull.input_parser import InputParser


def test_input_parser():
    file_name = "file.py"
    broker_url = "broker_url"
    local_host = "local_host"
    executors = "10"
    args = [
        "run",
        "--file",
        file_name,
        "--broker-url",
        broker_url,
        "--local-host",
        local_host,
        "--executors",
        executors,
    ]
    ip = InputParser()
    parsed = ip.parse_input(args)
    assert file_name == parsed.file
    assert broker_url == parsed.broker_url
    assert local_host == parsed.local_host
    assert executors == parsed.executors


def test_input_run_as_instance():
    file_name = "file.py"
    service_id = "service_id"
    instance_id = "instance_id"

    args = ["run", "--file", file_name, "as_instance", "--service-id", service_id, "--instance-id", instance_id]
    ip = InputParser()
    parsed = ip.parse_input(args)
    assert file_name == parsed.file
    assert service_id == parsed.service_id
    assert instance_id == parsed.instance_id


def test_input_defaults():
    file_name = "file.py"
    ip = InputParser()
    args = ["run", "--file", file_name]
    parsed = ip.parse_input(args)

    assert file_name == parsed.file
    assert "127.0.0.1:8080" == parsed.broker_url
    assert "127.0.0.1" == parsed.local_host
    assert 1 == parsed.executors
