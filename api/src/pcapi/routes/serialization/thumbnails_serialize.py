import flask

from pcapi.core.offers import validation
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.image_conversion import CropParams


class CreateThumbnailBodyModel(BaseModel):
    offer_id: int
    credit: str | None
    cropping_rect_x: float | None
    cropping_rect_y: float | None
    cropping_rect_height: float | None
    cropping_rect_width: float | None

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

    def get_image_as_bytes(self, request: flask.Request) -> bytes:
        """
        Get the image from the POSTed data (request)
        """
        if "thumb" in request.files:
            blob = request.files["thumb"]
            return blob.read()

        raise validation.exceptions.MissingImage()


class CreateThumbnailResponseModel(BaseModel):
    id: int
    url: str
    credit: str | None
