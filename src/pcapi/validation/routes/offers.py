from pcapi.domain.allocine import get_editable_fields_for_allocine_offers
from pcapi.models import Offer
from pcapi.models.api_errors import ApiErrors
from pcapi.models.offer_type import ProductType


def check_offer_type_is_valid(offer_type_name):
    if not ProductType.is_thing(offer_type_name) and not ProductType.is_event(offer_type_name):
        api_error = ApiErrors()
        api_error.add_error("type", "Le type de cette offre est inconnu")
        raise api_error


def check_offer_name_length_is_valid(offer_name: str):
    max_offer_name_length = 90
    if len(offer_name) > max_offer_name_length:
        api_error = ApiErrors()
        api_error.add_error("name", "Le titre de l’offre doit faire au maximum 90 caractères.")
        raise api_error


def check_offer_id_is_present_in_request(offer_id: str):
    if offer_id is None:
        errors = ApiErrors()
        errors.status_code = 400
        errors.add_error("global", "Le paramètre offerId est obligatoire")
        errors.maybe_raise()
        raise errors


def check_edition_for_allocine_offer_is_valid(payload: dict):
    editable_fields_for_offer = get_editable_fields_for_allocine_offers()

    all_payload_fields_are_editable = set(payload).issubset(editable_fields_for_offer)

    if not all_payload_fields_are_editable:
        list_of_non_editable_fields = set(payload).difference(editable_fields_for_offer)

        api_error = ApiErrors()
        for non_editable_field in list_of_non_editable_fields:
            api_error.add_error(non_editable_field, "Vous ne pouvez pas modifier ce champ")

        raise api_error
