import typing

from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import address_serialize

from . import utils


# TODO(jbaudet - 11/2025): remove once (pro) GET /venues has been
# migrated (-> minimum information returned)
class VenueListItemResponseModel(BaseModel, AccessibilityComplianceMixin):
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
    venueTypeCode: offerers_models.VenueTypeCode
    externalAccessibilityData: acceslibre_serializers.ExternalAccessibilityDataModel | None
    location: address_serialize.LocationResponseModel | None
    isPermanent: bool
    isCaledonian: bool
    isActive: bool
    isValidated: bool
    bankAccountStatus: utils.SimplifiedBankAccountStatus | None
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
            "bankAccountStatus": utils.parse_venue_bank_account_status(venue),
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
    ) -> acceslibre_serializers.ExternalAccessibilityDataModel | None:
        if not venue.accessibilityProvider:
            return None
        return acceslibre_serializers.ExternalAccessibilityDataModel.from_accessibility_infos(
            venue.accessibilityProvider.externalAccessibilityData
        )

    @classmethod
    def build_address(cls, venue: offerers_models.Venue) -> address_serialize.LocationResponseModel | None:
        offerer_address = venue.offererAddress
        if not offerer_address:
            return None
        data: dict[str, typing.Any] = {
            "id": offerer_address.addressId,
            "id_oa": offerer_address.id,
            "banId": offerer_address.address.banId,
            "inseeCode": offerer_address.address.inseeCode,
            "longitude": offerer_address.address.longitude,
            "latitude": offerer_address.address.latitude,
            "postalCode": offerer_address.address.postalCode,
            "street": offerer_address.address.street,
            "city": offerer_address.address.city,
            "label": venue.common_name,
            "isManualEdition": offerer_address.address.isManualEdition,
            "departmentCode": offerer_address.address.departmentCode,
            "isVenueLocation": True,
        }
        return address_serialize.LocationResponseModel(**data)


# TODO(jbaudet - 11/2025): remove once (pro) GET /venues has been
# migrated (-> minimum information returned)
class GetVenueListResponseModel(BaseModel):
    venues: list[VenueListItemResponseModel]
