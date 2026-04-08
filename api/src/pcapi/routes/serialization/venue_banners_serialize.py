import typing
from io import BytesIO

import pydantic as pydantic_v2
from PIL import Image
from pydantic import model_validator
from pydantic_core import PydanticCustomError

from pcapi.core.offerers import exceptions
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers.validation import VENUE_BANNER_MAX_SIZE
from pcapi.core.offers.validation import ACCEPTED_THUMBNAIL_FORMATS
from pcapi.routes.serialization import HttpBodyModel
from pcapi.utils.image_conversion import CropParamsV2
from pcapi.utils.image_conversion import CropPercent


class BannerMetaModel(HttpBodyModel):
    image_credit: (
        typing.Annotated[
            str,
            pydantic_v2.Field(max_length=offerers_schemas.VENUE_IMAGE_CREDIT_MAX_LENGTH),
        ]
        | None
    )
    original_image_url: str | None = None  # TODO: move to HttpUrl ?
    crop_params: CropParamsV2 = CropParamsV2()

    model_config = pydantic_v2.ConfigDict(
        alias_generator=None,
        extra="ignore",
    )


class VenueBannerContentModel(HttpBodyModel):
    model_config = pydantic_v2.ConfigDict(extra="ignore")
    content: typing.Annotated[
        bytes,
        pydantic_v2.Field(min_length=2, max_length=VENUE_BANNER_MAX_SIZE),
    ]
    image_credit: typing.Annotated[str, pydantic_v2.Field(min_length=1, max_length=255)] | None = None

    # cropping parameters must be a % (between 0 and 1) of the original
    # bottom right corner and the original height
    x_crop_percent: CropPercent = 0.0
    y_crop_percent: CropPercent = 0.0
    height_crop_percent: CropPercent = 1.0
    width_crop_percent: CropPercent = 1.0

    @model_validator(mode="before")
    @classmethod
    def validate_banner(cls, values: dict) -> dict:
        """
        Validate content (is not an invalid image) using PIL
        + set and validate content type using image build from previous
          step
        """
        try:
            image = Image.open(BytesIO(values["content"]))
        except Exception:
            raise PydanticCustomError("invalid_image_format", "Format de l'image invalide")

        content_type = image.format and image.format.lower()

        if content_type not in ACCEPTED_THUMBNAIL_FORMATS:
            raise PydanticCustomError("invalid_image_format", "Format de l'image invalide")

        return values

    @classmethod
    def from_request(cls, request: typing.Any) -> "VenueBannerContentModel":
        """
        If the request has a content_lenght information, use directly to
        avoid reading the whole content to check its size.
        """
        try:
            file = request.files["banner"]
        except (AttributeError, KeyError):
            raise exceptions.InvalidVenueBannerContent("Image manquante")

        if file.content_length and file.content_length > VENUE_BANNER_MAX_SIZE:
            raise exceptions.VenueBannerTooBig(f"Image trop grande, max: {VENUE_BANNER_MAX_SIZE / 1_000}Ko")

        return VenueBannerContentModel(
            content=file.read(VENUE_BANNER_MAX_SIZE),
            image_credit=request.args.get("image_credit"),
            x_crop_percent=request.args.get("x_crop_percent"),
            y_crop_percent=request.args.get("y_crop_percent"),
            height_crop_percent=request.args.get("height_crop_percent"),
            width_crop_percent=request.args.get("width_crop_percent"),
        )

    @property
    def crop_params(self) -> CropParamsV2 | None:
        if {self.x_crop_percent, self.y_crop_percent, self.height_crop_percent, self.width_crop_percent} == {None}:
            return None

        return CropParamsV2(
            x_crop_percent=self.x_crop_percent,
            y_crop_percent=self.y_crop_percent,
            height_crop_percent=self.height_crop_percent,
            width_crop_percent=self.width_crop_percent,
        )
