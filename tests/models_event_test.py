from models import Event, EventType


def test_an_event_is_always_physical_and_cannot_be_digital():
    assert Event().isDigital is False


def test_event_type_find_from_sub_labels_returns_nothing_if_no_sub_labels():
    # given
    sub_labels = []

    # when
    types = EventType.find_from_sub_labels(sub_labels)

    # then
    assert types == []


def test_event_type_find_from_sub_labels_returns_nothing_if_label_is_unknown():
    # given
    sub_labels = ['randomlabel']

    # when
    types = EventType.find_from_sub_labels(sub_labels)

    # then
    assert types == []


def test_event_type_find_from_sub_labels_returns_several_types_given_several_sub_labels_ignoring_case():
    # given
    sub_labels = ['Regarder', 'appLAuDIr']

    # when
    types = EventType.find_from_sub_labels(sub_labels)

    # then
    assert len(types) == 3
    assert EventType.CINEMA in types
    assert EventType.MUSEES_PATRIMOINE in types
    assert EventType.SPECTACLE_VIVANT in types
