from pcapi.core.offers import validation
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.image_conversion import CropParams


class CreateThumbnailBodyModel(BaseModel):
    offer_id: int
    credit: str | None
    cropping_rect_x: float | None
    cropping_rect_y: float | None
    cropping_rect_height: float | None
    cropping_rect_width: float | None

    _dehumanize_offer_id = dehumanize_field("offer_id")

    class Config:
        alias_generator = to_camel

    @property
    def crop_params(self) -> CropParams | None:
        if {self.cropping_rect_x, self.cropping_rect_y, self.cropping_rect_height, self.cropping_rect_width} == {None}:
            return None

        return CropParams.build(
            x_crop_percent=self.cropping_rect_x,
            y_crop_percent=self.cropping_rect_y,
            height_crop_percent=self.cropping_rect_height,
            width_crop_percent=self.cropping_rect_width,
        )

    def get_image_as_bytes(self, request) -> bytes:  # type: ignore [no-untyped-def]
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
