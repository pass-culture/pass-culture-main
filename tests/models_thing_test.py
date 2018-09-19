from models import ThingType


def test_thing_type_find_from_sub_labels_returns_nothing_if_no_sub_labels():
    # given
    sub_labels = []

    # when
    types = ThingType.find_from_sub_labels(sub_labels)

    # then
    assert types == []


def test_thing_type_find_from_sub_labels_returns_nothing_if_label_is_unknown():
    # given
    sub_labels = ['randomlabel']

    # when
    types = ThingType.find_from_sub_labels(sub_labels)

    # then
    assert types == []


def test_thing_type_find_from_sub_labels_returns_several_types_given_several_sub_labels_ignoring_case():
    # given
    sub_labels = ['Regarder', 'LIRE']

    # when
    types = ThingType.find_from_sub_labels(sub_labels)

    # then
    assert len(types) == 5
    assert ThingType.AUDIOVISUEL in types
    assert ThingType.CINEMA_ABO in types
    assert ThingType.MUSEES_PATRIMOINE_ABO in types
    assert ThingType.LIVRE_EDITION in types
    assert ThingType.PRESSE_ABO in types
