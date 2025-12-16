import re
from typing import Literal

import pydantic as pydantic_v2
from pydantic import AfterValidator
from typing_extensions import Annotated

from pcapi.core.categories import subcategories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models


# -------------------------------------------------------------------- #
# ------------------------------ SHARED ------------------------------ #
# -------------------------------------------------------------------- #


class ExtraData(pydantic_v2.BaseModel):
    ean: str
    model_config = pydantic_v2.ConfigDict(extra="ignore")


def is_record_store(venue: offerers_models.Venue):
    return venue.venueTypeCode != offerers_schemas.VenueTypeCode.RECORD_STORE


# -------------------------------------------------------------------- #
# -------------------------------- V1 -------------------------------- #
# -------------------------------------------------------------------- #


# class InputData(pydantic_v2.BaseModel):
    # name: str
    # subcategory: subcategories.Subcategory
    # venueId: int
    # audioDisabilityCompliant: bool
    # mentalDisabilityCompliant: bool
    # motorDisabilityCompliant: bool
    # visualDisabilityCompliant: bool

    # # productId: int | None = None
    # # extraData: ExtraData | None = None

    # # @model_validator(mode='after')
    # # def tmp(self) -> Self:
    # # return self

    # model_config = pydantic_v2.ConfigDict(
        # str_strip_whitespace=True,
        # extra="forbid",
    # )


# class CreateData(pydantic_v2.BaseModel):
    # # input data
    # name: str
    # subcategory: subcategories.Subcategory
    # venueId: int
    # audioDisabilityCompliant: bool
    # mentalDisabilityCompliant: bool
    # motorDisabilityCompliant: bool
    # visualDisabilityCompliant: bool

    # productId: int | None = None
    # extraData: ExtraData | None = None

    # # context data
    # venue: offerers_models.Venue
    # product: models.Product | None = None


# class WithProduct(InputData):
    # product: models.Product


# class WithCDProduct(WithProduct):
    # subcategory: subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD
    # venue: Annotated[offerers_models.Venue, AfterValidator(is_record_store)]


# class CreateError(Exception):
    # def __init__(self, parsed_data):
        # self.parsed_data
        # super().__init__()


# class ProductIsMandatory(CreateError):
    # pass


# from typing_extensions import Self
# class Validator:
# def __init__(self, data, product, venue):
# self.data = data
# self.product = product
# self.venue = venue

# def validate_input(cls, data):
# try:
# return CreateThingWithEanData(**data)
# except (ValueError, TypeError):
# raise

# def validate_product(self, parsed_data):
# is_record_store = self.venue.venueTypeCode == VenueTypeCode.RECORD_STORE
# is_cd = parsed_data.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD

# if is_record_store and is_cd and not product:
# raise ProductIsMandatory(parsed_data)


# -------------------------------------------------------------------- #
# -------------------------------- V2 -------------------------------- #
# -------------------------------------------------------------------- #

# OfferName = ConstrainedStr = Annotated[str, StringConstraints(min_length=1, max_length=128, pattern=r"(?!\d{13})")]


class ProviderData(pydantic_v2.BaseModel):
    id_at_provider: str
    provider_id: int


class Venue(pydantic_v2.BaseModel):
    id: int
    code: offerers_schemas.VenueTypeCode


class Product(pydantic_v2.BaseModel):
    id: int


def does_not_contain_ean(name: str) -> str:
    if re.search(r"\d{13}", name):
        raise ValueError(name)



class SharedInput(pydantic_v2.BaseModel):
    name: Annotated[str, AfterValidator(does_not_contain_ean)]
    venue: Venue
    audioDisabilityCompliant: bool
    mentalDisabilityCompliant: bool
    motorDisabilityCompliant: bool
    visualDisabilityCompliant: bool

    productId: int | None = None
    extraData: ExtraData | None = None

    provider_data: ProviderData | None = None

    model_config = pydantic_v2.ConfigDict(
        # arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        extra="forbid",
    )


class LivrePapierModel(SharedInput):
    subcategoryId: Literal[subcategories.LIVRE_PAPIER.id]


class VinyleModel(SharedInput):
    subcategoryId: Literal[subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE]


class CDModel(SharedInput):
    subcategoryId: Literal[subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id]
    product: Product
    venue: Annotated[Venue, AfterValidator(is_record_store)]
