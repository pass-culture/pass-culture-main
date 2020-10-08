import pytest

from models import ApiErrors, ThingType
from repository import repository
import pytest
from model_creators.specific_creators import create_product_with_thing_type


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
    sub_labels = ['Regarder', 'LIRE', 'Pratiquer']

    # when
    types = ThingType.find_from_sub_labels(sub_labels)

    # then
    assert len(types) == 10
    assert ThingType.CINEMA_CARD in types
    assert ThingType.AUDIOVISUEL in types
    assert ThingType.CINEMA_ABO in types
    assert ThingType.MUSEES_PATRIMOINE_ABO in types
    assert ThingType.LIVRE_EDITION in types
    assert ThingType.PRESSE_ABO in types
    assert ThingType.PRATIQUE_ARTISTIQUE_ABO in types
    assert ThingType.OEUVRE_ART in types
    assert ThingType.INSTRUMENT in types


@pytest.mark.usefixtures("db_session")
def test_thing_error_when_thing_type_is_offlineOnly_but_has_url(app):
    # Given
    thing_product = create_product_with_thing_type(thing_type=ThingType.JEUX, url='http://mygame.fr/offre')

    # When
    with pytest.raises(ApiErrors) as errors:
        repository.save(thing_product)

    # Then
    assert errors.value.errors['url'] == ['Une offre de type Jeux (support physique) ne peut pas être numérique']


def test_thing_offerType_returns_dict_matching_ThingType_enum():
    # given
    thing_product = create_product_with_thing_type(thing_type=ThingType.LIVRE_EDITION)
    expected_value = {
        'conditionalFields': ["author", "isbn"],
        'proLabel': 'Livres papier ou numérique, abonnements lecture',
        'appLabel': 'Livre ou carte lecture',
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': 'Lire',
        'description': 'S’abonner à un quotidien d’actualité ?'
                       ' À un hebdomadaire humoristique ? '
                       'À un mensuel dédié à la nature ? '
                       'Acheter une BD ou un manga ? '
                       'Ou tout simplement ce livre dont tout le monde parle ?',
        'value': 'ThingType.LIVRE_EDITION',
        'type': 'Thing',
        'isActive': True
    }

    # when
    offer_type = thing_product.offerType

    # then
    assert offer_type == expected_value


def test_thing_offerType_returns_None_if_type_does_not_match_ThingType_enum():
    # given
    thing_product = create_product_with_thing_type(thing_type='')

    # when
    offer_type = thing_product.offerType

    # then
    assert offer_type == None
