import typing
from io import BytesIO

import pydantic
from pydantic import model_validator
import pydantic.v1 as pydantic_v1
from PIL import Image
from pydantic.v1 import root_validator
from pydantic.v1 import validator

from pcapi.core.offerers import exceptions
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers.validation import VENUE_BANNER_MAX_SIZE
from pcapi.core.offers.validation import ACCEPTED_THUMBNAIL_FORMATS
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.utils.image_conversion import CropParam
from pcapi.utils.image_conversion import CropPercent
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import CropParamsV2


class BannerMetaModelV2(HttpBodyModel):
    # TODO bulle: a supprimer
    original_image_url: str | None = None  # TODO: move to HttpUrl ?
    crop_params: CropParamsV2 = CropParamsV2()

    model_config = pydantic.ConfigDict(
        alias_generator=None,
        extra="ignore",
    )

    # @pydantic.field_validator("crop_params", mode="")
    # def validate_crop_params(cls, raw_crop_params: CropParamsV2 | None) -> CropParamsV2:
    #     """
    #     Old venues might have a crop_params key with a null value
    #     """
    #     if not raw_crop_params:
    #         return CropParamsV2()
    #     return raw_crop_params


class BannerMetaModel(BaseModel):
    image_credit: offerers_schemas.VenueImageCredit | None = None
    original_image_url: str | None = None
    crop_params: CropParams = CropParams()

    @validator("crop_params", pre=True)
    @classmethod
    def validate_crop_params(cls, raw_crop_params: CropParams | None) -> CropParams:
        """
        Old venues might have a crop_params key with a null value
        """
        if not raw_crop_params:
            return CropParams()
        return raw_crop_params


# TODO bulle chgt de banniere recoit toue la venue juste pour une image, normal?
class VenueBannerContentModel(HttpBodyModel):
    # TODO bulle: a supprimer?
    model_config = pydantic.ConfigDict(extra="ignore")
    content: typing.Annotated[
        bytes,
        pydantic.Field(min_length=2, max_length=VENUE_BANNER_MAX_SIZE),
    ]
    image_credit: (
        typing.Annotated[
            str, pydantic.AfterValidator(lambda x: str.strip(x)), pydantic.Field(min_length=1, max_length=255)
        ]
        | None
    ) = None

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
            raise ValueError("Format de l'image invalide")
        assert image.format is not None  # helps mypy

        content_type = image.format.lower()

        if content_type not in ACCEPTED_THUMBNAIL_FORMATS:
            raise ValueError("Format de l'image invalide")

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
