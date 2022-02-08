from typing import Optional

from pcapi.core.offers import validation
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel


class CreateThumbnailBodyModel(BaseModel):
    offer_id: int
    credit: Optional[str]
    cropping_rect_x: Optional[float]
    cropping_rect_y: Optional[float]
    cropping_rect_height: Optional[float]

    _dehumanize_offer_id = dehumanize_field("offer_id")

    class Config:
        alias_generator = to_camel

    @property
    def crop_params(self):
        if {self.cropping_rect_x, self.cropping_rect_y, self.cropping_rect_height} == {None}:
            return None
        return (self.cropping_rect_x, self.cropping_rect_y, self.cropping_rect_height)

    def get_image_as_bytes(self, request) -> bytes:
        """
        Get the image from the POSTed data (request)
        Only the max size is checked at this stage, and possibly the content type header
        """
        if "thumb" in request.files:
            blob = request.files["thumb"]
            image_as_bytes = blob.read()
            return validation.get_uploaded_image(image_as_bytes)

        raise validation.exceptions.MissingImage()


class CreateThumbnailResponseModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")
