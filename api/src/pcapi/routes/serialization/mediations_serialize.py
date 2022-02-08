from datetime import datetime
import logging
from pathlib import Path
from typing import Optional

from pydantic import Field

from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils import requests
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


ALLOWED_IMAGE_SUFFIXES = {".gif", ".jpg", ".jpeg", ".png"}


class CreateMediationBodyModel(BaseModel):
    thumb_url: Optional[str]
    offerer_id: int
    offer_id: int
    credit: Optional[str]
    cropping_rect_x: Optional[float] = Field(None, alias="croppingRect[x]")
    cropping_rect_y: Optional[float] = Field(None, alias="croppingRect[y]")
    cropping_rect_height: Optional[float] = Field(None, alias="croppingRect[height]")

    _dehumanize_offerer_id = dehumanize_field("offerer_id")
    _dehumanize_offer_id = dehumanize_field("offer_id")

    class Config:
        alias_generator = to_camel

    @property
    def crop_params(self):
        if {self.cropping_rect_x, self.cropping_rect_y, self.cropping_rect_height} == {None}:
            return None
        return (self.cropping_rect_x, self.cropping_rect_y, self.cropping_rect_height)

    def get_image_as_bytes(self, request):
        """Get the image from the POSTed data (request) or from the form field
        (in which case it's supposed to be an URL that we are going to
        request.
        """
        # FIXME: use pydantic logic to return validation errors
        missing_image_error = ApiErrors({"thumb": ["Vous devez fournir une image d'accroche"]})

        if "thumb" in request.files:
            blob = request.files["thumb"]
            if not blob.filename:
                raise missing_image_error
            if Path(blob.filename).suffix not in ALLOWED_IMAGE_SUFFIXES:
                error = (
                    f"Cette image n'a pas d'extension ({', '.join(ALLOWED_IMAGE_SUFFIXES)}) "
                    f"ou son format n'est pas autorisé"
                )
                raise ApiErrors({"thumb": [error]})

            return blob.read()

        if self.thumb_url:
            try:
                return _fetch_image(self.thumb_url)
            except ValueError as value_error:
                logger.exception(value_error)
                raise ApiErrors({"thumbUrl": ["L'adresse saisie n'est pas valide"]})

        raise missing_image_error


def _fetch_image(url: str) -> bytes:
    if not url[0:4] == "http":
        raise ValueError("Invalid URL: %s" % url)

    try:
        response = requests.get(url)
    except Exception as error:
        logger.exception("Could not download image at %s: %s", url, error)
        raise ApiErrors({"thumbUrl": ["Impossible de télécharger l'image à cette adresse"]})

    content_type = response.headers.get("Content-type", "")
    if response.status_code != 200 or not content_type.startswith("image/"):
        raise ValueError(
            "Got status_code=%s, content_type=%s when downloading thumb from url=%s"
            % (response.status_code, content_type, url)
        )

    return response.content


class MediationResponseIdModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class UpdateMediationResponseModel(BaseModel):
    authorId: Optional[str]
    credit: Optional[str]
    dateCreated: Optional[datetime]
    dateModifiedAtLastProvider: Optional[datetime]
    fieldsUpdated: Optional[list[str]]
    id: str
    idAtProviders: Optional[str]
    isActive: bool
    lastProviderId: Optional[str]
    offerId: Optional[str]
    thumbCount: int
    thumbUrl: Optional[str]

    _humanize_id = humanize_field("id")
    _humanize_author_id = humanize_field("authorId")
    _humanize_id_at_providers = humanize_field("idAtProviders")
    _humanize_last_provider_id = humanize_field("lastProviderId")
    _humanize_offer_id = humanize_field("offerId")

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True


class UpdateMediationBodyModel(BaseModel):
    isActive: bool
