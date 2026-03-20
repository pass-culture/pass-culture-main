import typing
from io import BytesIO

import pydantic
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
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import CropParamsV2


class BannerMetaModelV2(HttpBodyModel):
    original_image_url: str | None = None  # TODO: move to HttpUrl ?
    crop_params: CropParamsV2 = CropParamsV2()

    model_config = pydantic.ConfigDict(
        alias_generator=None,
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


class VenueBannerContentModel(BaseModel):
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        content: bytes
    else:
        content: pydantic_v1.conbytes(min_length=2, max_length=VENUE_BANNER_MAX_SIZE)
    image_credit: offerers_schemas.VenueImageCredit | None

    # cropping parameters must be a % (between 0 and 1) of the original
    # bottom right corner and the original height
    x_crop_percent: CropParam
    y_crop_percent: CropParam
    height_crop_percent: CropParam
    width_crop_percent: CropParam

    class Config:
        extra = pydantic_v1.Extra.forbid
        anystr_strip_whitespace = True

    @root_validator(pre=True)
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
        cls.validate_request(request)

        file = request.files["banner"]
        return VenueBannerContentModel(
            content=file.read(VENUE_BANNER_MAX_SIZE),
            image_credit=request.args.get("image_credit"),
            x_crop_percent=request.args.get("x_crop_percent"),
            y_crop_percent=request.args.get("y_crop_percent"),
            height_crop_percent=request.args.get("height_crop_percent"),
            width_crop_percent=request.args.get("width_crop_percent"),
        )

    @classmethod
    def validate_request(cls, request: typing.Any) -> typing.Any:
        """
        If the request has a content_lenght information, use directly to
        avoid reading the whole content to check its size. If not, do not
        consider this a an error: it will be checked later.
        """
        try:
            file = request.files["banner"]
        except (AttributeError, KeyError):
            raise exceptions.InvalidVenueBannerContent("Image manquante")

        if file.content_length and file.content_length > VENUE_BANNER_MAX_SIZE:
            raise exceptions.VenueBannerTooBig(f"Image trop grande, max: {VENUE_BANNER_MAX_SIZE / 1_000}Ko")

        return request

    @property
    def crop_params(self) -> CropParams | None:
        if {self.x_crop_percent, self.y_crop_percent, self.height_crop_percent, self.width_crop_percent} == {None}:
            return None

        return CropParams(
            x_crop_percent=self.x_crop_percent,
            y_crop_percent=self.y_crop_percent,
            height_crop_percent=self.height_crop_percent,
            width_crop_percent=self.width_crop_percent,
        )
