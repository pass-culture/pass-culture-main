import re

from pydantic.v1 import HttpUrl

from pcapi.models.api_errors import ApiErrors


def check_offer_name_length_is_valid(offer_name: str) -> None:
    max_offer_name_length = 90
    if len(offer_name) > max_offer_name_length:
        api_error = ApiErrors()
        api_error.add_error("name", "Le titre de l’offre doit faire au maximum 90 caractères.")
        raise api_error


def check_video_url(video_url: HttpUrl | None) -> None:
    if not video_url:
        return
    youtube_pattern = re.compile(
        r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]{11})"
    )

    is_youtube = youtube_pattern.match(video_url)

    if not is_youtube:
        raise ApiErrors(errors={"videoUrl": ["Veuillez renseigner une url provenant de la plateforme Youtube"]})
