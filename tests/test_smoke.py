from integration_factory.state import IntegrationState


def test_state_builds():
    state = IntegrationState(vendor="acme", raw_docs="openapi: 3.0.0")
    assert state.iteration == 0
    assert state.assumptions == []
