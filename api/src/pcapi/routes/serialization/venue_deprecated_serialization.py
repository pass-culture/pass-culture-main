import typing

import pydantic as pydantic_v2

from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import venue_finance_serialize


def parse_venue_type_code(venue_type_code: str | offerers_schemas.VenueTypeCode) -> offerers_schemas.VenueTypeCodeKey:
    if isinstance(venue_type_code, str):
        return offerers_schemas.VenueTypeCodeKey[venue_type_code]
    return offerers_schemas.VenueTypeCodeKey[venue_type_code.name]


# TODO(jbaudet - 11/2025): remove once (pro) GET /venues has been
# migrated (-> minimum information returned)
class VenueListItemResponseModel(HttpBodyModel):
    audioDisabilityCompliant: bool | None
    mentalDisabilityCompliant: bool | None
    motorDisabilityCompliant: bool | None
    visualDisabilityCompliant: bool | None
    id: int
    managingOffererId: int
    name: str
    offererName: str
    publicName: str
    isVirtual: bool
    bookingEmail: str | None
    withdrawalDetails: str | None
    siret: str | None
    hasCreatedOffer: bool
    venueTypeCode: typing.Annotated[
        offerers_schemas.VenueTypeCodeKey, pydantic_v2.BeforeValidator(parse_venue_type_code)
    ]
    externalAccessibilityData: acceslibre_serializers.ExternalAccessibilityDataModelV2 | None
    location: address_serialize.LocationResponseModelV2 | None
    isPermanent: bool
    isCaledonian: bool
    isActive: bool
    isValidated: bool
    bankAccountStatus: venue_finance_serialize.SimplifiedBankAccountStatus | None
    hasNonFreeOffers: bool

    @classmethod
    def build(
        cls,
        venue: offerers_models.Venue,
        ids_of_venues_with_offers: typing.Iterable[int] = (),
        venues_with_non_free_offers: set[int] = set(),
    ) -> "VenueListItemResponseModel":
        # map model fields (direct and inherited) to exact same venue fields
        direct_mapping_venue_fields = {
            field: getattr(venue, field) for field in cls.schema()["properties"].keys() if hasattr(venue, field)
        }

        # compute other missing model fields (direct and inherited)
        extra = {
            "offererName": venue.managingOfferer.name,
            "hasCreatedOffer": venue.id in ids_of_venues_with_offers,
            "externalAccessibilityData": cls.build_external_accessibility_data(venue),
            "location": cls.build_address(venue),
            "isCaledonian": venue.is_caledonian,
            "isActive": venue.managingOfferer.isActive,
            "isValidated": venue.managingOfferer.isValidated,
            "bankAccountStatus": venue_finance_serialize.parse_venue_bank_account_status(venue),
            "hasNonFreeOffers": venue.id in venues_with_non_free_offers,
        }

        # building a dict and expanding it after using ** is not needed
        # but mypy disagrees: it sees two parameters sent instead of
        # many kwargs
        mypy_friendly_kwargs = {**direct_mapping_venue_fields, **extra}
        return cls(**mypy_friendly_kwargs)

    @classmethod
    def build_external_accessibility_data(
        cls, venue: offerers_models.Venue
    ) -> acceslibre_serializers.ExternalAccessibilityDataModelV2 | None:
        if not venue.accessibilityProvider:
            return None
        return acceslibre_serializers.ExternalAccessibilityDataModelV2.from_accessibility_infos(
            venue.accessibilityProvider.externalAccessibilityData
        )

    @classmethod
    def build_address(cls, venue: offerers_models.Venue) -> address_serialize.LocationResponseModelV2 | None:
        offerer_address = venue.offererAddress
        if not offerer_address:
            return None
        return address_serialize.LocationResponseModelV2.build(
            offerer_address, label=venue.publicName, is_venue_location=True
        )


# TODO(jbaudet - 11/2025): remove once (pro) GET /venues has been
# migrated (-> minimum information returned)
class GetVenueListResponseModel(HttpBodyModel):
    venues: list[VenueListItemResponseModel]
