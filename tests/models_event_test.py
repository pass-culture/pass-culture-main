from models import Event, EventType
from utils.test_utils import create_event


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


def test_event_type_enum_returns_enum_matching_type():
    # given
    event = create_event(event_type=EventType.SPECTACLE_VIVANT)

    # when
    enum_type = event.enum_type

    # then
    assert enum_type == EventType.SPECTACLE_VIVANT


def test_event_type_enum_returns_information_in_type_if_does_not_match_enum():
    # given
    event = create_event(event_type='Workshop')

    # when
    enum_type = event.enum_type

    # then
    assert enum_type == 'Workshop'
