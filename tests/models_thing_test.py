import pytest

from models import PcObject, ApiErrors, ThingType
from tests.conftest import clean_database
from tests.test_utils import create_thing


def test_thing_type_find_from_sub_labels_returns_nothing_if_no_sub_labels():
    # given
    sub_labels = []

    # when
    types = ThingType.find_from_sub_labels(sub_labels)

    # then
    assert types == []


@pytest.mark.standalone
def test_thing_type_find_from_sub_labels_returns_nothing_if_label_is_unknown():
    # given
    sub_labels = ['randomlabel']

    # when
    types = ThingType.find_from_sub_labels(sub_labels)

    # then
    assert types == []


@pytest.mark.standalone
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


@clean_database
@pytest.mark.standalone
def test_thing_error_when_thing_type_is_offlineOnly_but_has_url(app):
    # Given
    thing = create_thing(thing_type=ThingType.JEUX, url='http://mygame.fr/offre')

    # When
    with pytest.raises(ApiErrors) as errors:
        PcObject.check_and_save(thing)

    # Then
    assert errors.value.errors['url'] == ['Une offre de type Jeux (Biens physiques) ne peut pas être numérique']


def test_thing_offerType_returns_dict_matching_ThingType_enum():
    # given
    thing = create_thing(thing_type=ThingType.LIVRE_EDITION)
    expected_value = {
        'label': 'Livre — Édition',
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': 'Lire',
        'description': 'S’abonner à un quotidien d’actualité ?'
                       ' À un hebdomadaire humoristique ? '
                       'À un mensuel dédié à la nature ? '
                       'Acheter une BD ou un manga ? '
                       'Ou tout simplement ce livre dont tout le monde parle ?',
        'value': 'ThingType.LIVRE_EDITION',
        'type': 'Thing'
    }

    # when
    offer_type = thing.offerType

    # then
    assert offer_type == expected_value


def test_thing_offerType_returns_None_if_type_does_not_match_ThingType_enum():
    # given
    thing = create_thing(thing_type='')

    # when
    offer_type = thing.offerType

    # then
    assert offer_type == None
