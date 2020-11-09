from pcapi.model_creators.specific_creators import create_product_with_event_type
from pcapi.models import EventType
from pcapi.models import Product


def test_an_event_is_always_physical_and_cannot_be_digital():
    assert Product().isDigital is False


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
    sub_labels = ['Activation', 'Regarder', 'appLAuDIr', 'PRATIQUER']

    # when
    types = EventType.find_from_sub_labels(sub_labels)

    # then
    assert len(types) == 5
    assert EventType.ACTIVATION in types
    assert EventType.CINEMA in types
    assert EventType.MUSEES_PATRIMOINE in types
    assert EventType.SPECTACLE_VIVANT in types


def test_event_offerType_returns_dict_matching_EventType_enum():
    # given
    event_product = create_product_with_event_type(event_type=EventType.SPECTACLE_VIVANT)
    expected_value = {
        'conditionalFields': ["author", "showType", "stageDirector", "performer"],
        'proLabel': "Spectacle vivant",
        'appLabel': "Spectacle",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Applaudir",
        'description': "Suivre un géant de 12 mètres dans la ville ? "
                       "Rire aux éclats devant un stand up ?"
                       " Rêver le temps d’un opéra ou d’un spectacle de danse ? "
                       "Assister à une pièce de théâtre, ou se laisser conter une histoire ?",
        'value': 'EventType.SPECTACLE_VIVANT',
        'type': 'Event',
        'isActive': True
    }

    # when
    offer_type = event_product.offerType

    # then
    assert offer_type == expected_value


def test_event_offerType_returns_None_if_type_does_not_match_EventType_enum():
    # given
    event_product = create_product_with_event_type(event_type='Workshop')

    # when
    offer_type = event_product.offerType

    # then
    assert offer_type == None
