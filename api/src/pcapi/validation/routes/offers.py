from pydantic.v1 import HttpUrl

from pcapi.core.offers import api
from pcapi.core.offers import models
from pcapi.models.api_errors import ApiErrors


def check_offer_name_length_is_valid(offer_name: str) -> None:
    max_offer_name_length = 90
    if len(offer_name) > max_offer_name_length:
        api_error = ApiErrors()
        api_error.add_error("name", "Le titre de l’offre doit faire au maximum 90 caractères.")
        raise api_error


def check_video_url(video_url: HttpUrl | None) -> str | None:
    if not video_url:
        return None

    video_id = api.extract_youtube_video_id(video_url)
    if not video_id:
        raise ApiErrors(errors={"videoUrl": ["Veuillez renseigner une URL provenant de la plateforme Youtube"]})
    return video_id


def check_offer_can_ask_for_highlight_request(offer: models.Offer) -> None:
    if not offer.isEvent:
        raise ApiErrors(
            errors={"global": ["La sous catégorie de l'offre ne lui permet pas de participer à un temps fort"]}
        )
