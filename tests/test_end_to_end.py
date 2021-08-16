import pytest 

@pytest.mark.skip()
def test_message_simulation(sample_data, session):
    local_session = session()

    for pair in sample_data:
        _ = local_session.send(pair["req"].dump())
        local_session.recv()
