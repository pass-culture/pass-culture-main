from pcapi.core.categories import subcategories
from pcapi.model_creators.specific_creators import create_product_with_event_subcategory
from pcapi.models import Product


def test_an_event_is_always_physical_and_cannot_be_digital():
    assert Product().isDigital is False


def test_event_offerType_returns_dict_matching_EventType_enum():
    # given
    event_product = create_product_with_event_subcategory(
        event_subcategory_id=subcategories.SPECTACLE_REPRESENTATION.id,
    )
    expected_value = {
        "conditionalFields": ["author", "showType", "stageDirector", "performer"],
        "proLabel": "Spectacle vivant",
        "appLabel": "Spectacle",
        "offlineOnly": True,
        "onlineOnly": False,
        "sublabel": "Applaudir",
        "description": "Suivre un géant de 12 mètres dans la ville ? "
        "Rire aux éclats devant un stand up ?"
        " Rêver le temps d’un opéra ou d’un spectacle de danse ? "
        "Assister à une pièce de théâtre, ou se laisser conter une histoire ?",
        "value": "EventType.SPECTACLE_VIVANT",
        "type": "Event",
        "isActive": True,
    }

    # when
    offer_type = event_product.offerType

    # then
    assert offer_type == expected_value


def test_event_offerType_returns_None_if_type_does_not_match_EventType_enum():
    # given
    event_product = create_product_with_event_subcategory(event_subcategory_id="Workshop")

    # when
    offer_type = event_product.offerType

    # then
    assert offer_type == None
