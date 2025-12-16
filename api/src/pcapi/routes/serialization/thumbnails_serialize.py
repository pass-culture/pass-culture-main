import pydantic as pydantic_v2

from pcapi.routes.serialization import HttpBodyModel
from pcapi.utils.image_conversion import CropParams


class CreateThumbnailBodyModel(HttpBodyModel):
    offer_id: int
    credit: str | None = None
    cropping_rect_x: float | None = None
    cropping_rect_y: float | None = None
    cropping_rect_height: float | None = None
    cropping_rect_width: float | None = None

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

    # this model is applied to a form and some fields are not checked by the serializer
    model_config = pydantic_v2.ConfigDict(extra="ignore")


class CreateThumbnailResponseModel(HttpBodyModel):
    id: int
    thumbUrl: str = pydantic_v2.Field(alias="url")
    credit: str | None = None
