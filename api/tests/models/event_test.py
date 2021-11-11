from pcapi.models import Product


def test_an_event_is_always_physical_and_cannot_be_digital():
    assert Product().isDigital is False
