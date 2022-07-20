from datetime import datetime

from pcapi import settings
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.repository as offerers_repository
import pcapi.core.users.models as users_models
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import venues_serialize
from pcapi.serialization.utils import humanize_field
import pcapi.utils.date as date_utils


class GetOffererVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    address: str | None
    bookingEmail: str | None
    businessUnitId: int | None
    city: str | None
    comment: str | None
    departementCode: str | None
    id: str
    isValidated: bool
    isVirtual: bool
    managingOffererId: str
    name: str
    nonHumanizedId: int
    postalCode: str | None
    publicName: str | None
    siret: str | None
    venueLabelId: str | None
    withdrawalDetails: str | None
    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_venue_label_id = humanize_field("venueLabelId")

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "GetOffererVenueResponseModel":
        venue.nonHumanizedId = venue.id
        return super().from_orm(venue)

    class Config:
        orm_mode = True
        json_encoders = {datetime: date_utils.format_into_utc_date}


class OffererApiKey(BaseModel):
    maxAllowed: int
    prefixes: list[str]


class GetOffererResponseModel(BaseModel):
    address: str | None
    apiKey: OffererApiKey
    bic: str | None
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: datetime | None
    demarchesSimplifieesApplicationId: str | None
    fieldsUpdated: list[str]
    hasAvailablePricingPoints: bool
    hasDigitalVenueAtLeastOneOffer: bool
    hasMissingBankInformation: bool
    iban: str | None
    id: str
    idAtProviders: str | None
    isValidated: bool
    isActive: bool
    lastProviderId: str | None
    managedVenues: list[GetOffererVenueResponseModel]
    name: str
    nonHumanizedId: int
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: str | None

    _humanize_id = humanize_field("id")

    @classmethod
    def from_orm(cls, offerer: offerers_models.Offerer, venue_stats_by_ids: dict[int, venues_serialize.VenueStatsResponseModel] | None = None):  # type: ignore
        offerer.apiKey = {
            "maxAllowed": settings.MAX_API_KEY_PER_OFFERER,
            "prefixes": offerers_repository.get_api_key_prefixes(offerer.id),
        }
        if venue_stats_by_ids:
            for managedVenue in offerer.managedVenues:
                managedVenue.stats = venue_stats_by_ids[managedVenue.id]

        offerer.hasDigitalVenueAtLeastOneOffer = offerers_repository.has_digital_venue_with_at_least_one_offer(
            offerer.id
        )
        offerer.hasMissingBankInformation = not offerer.demarchesSimplifieesApplicationId and (
            offerers_repository.has_physical_venue_without_draft_or_accepted_bank_information(offerer.id)
            or offerer.hasDigitalVenueAtLeastOneOffer
        )
        offerer.hasAvailablePricingPoints = any(venue.siret for venue in offerer.managedVenues)
        offerer.nonHumanizedId = offerer.id

        return super().from_orm(offerer)

    class Config:
        orm_mode = True
        json_encoders = {datetime: date_utils.format_into_utc_date}


class GetOffererNameResponseModel(BaseModel):
    id: str
    name: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetOfferersNamesResponseModel(BaseModel):
    offerersNames: list[GetOffererNameResponseModel]

    class Config:
        orm_mode = True


class GetOfferersNamesQueryModel(BaseModel):
    validated: bool | None
    # FIXME (dbaty, 2022-05-04): rename to something clearer, e.g. `include_non_validated_user_offerers`
    validated_for_user: bool | None

    class Config:
        extra = "forbid"


class GetEducationalOffererVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    address: str | None
    city: str | None
    id: str
    isVirtual: bool
    publicName: str | None
    name: str
    postalCode: str | None
    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetEducationalOffererResponseModel(BaseModel):
    id: str
    name: str
    managedVenues: list[GetEducationalOffererVenueResponseModel]

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetEducationalOfferersResponseModel(BaseModel):
    educationalOfferers: list[GetEducationalOffererResponseModel]

    class Config:
        orm_mode = True


class GetEducationalOfferersQueryModel(BaseModel):
    offerer_id: str | None

    class Config:
        extra = "forbid"


class GenerateOffererApiKeyResponse(BaseModel):
    apiKey: str


class CreateOffererQueryModel(BaseModel):
    address: str | None
    city: str
    latitude: float | None
    longitude: float | None
    name: str
    postalCode: str
    siren: str

    class Config:
        extra = "forbid"
        anystr_strip_whitespace = True


class GetOfferersVenueResponseModel(BaseModel):
    id: str
    isVirtual: bool
    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetOfferersResponseModel(BaseModel):
    id: str
    name: str
    # FIXME (mageoffray, 2021-12-27): optional until we populate the database (PC-5693)
    siren: str | None
    isValidated: bool
    userHasAccess: bool
    nOffers: int  # possibly `-1` for offerers with too much offers.
    managedVenues: list[GetOfferersVenueResponseModel]

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(  # type: ignore [no-untyped-def, override]
        cls,
        offerer: offerers_models.Offerer,
        user: users_models.User,
        offer_counts: dict[int, int],
    ):
        offerer.userHasAccess = user.has_admin_role or any(
            uo.isValidated for uo in offerer.UserOfferers if uo.userId == user.id
        )
        venue_ids = (venue.id for venue in offerer.managedVenues)
        offerer.nOffers = sum((offer_counts.get(venue_id, 0) for venue_id in venue_ids), 0)
        return super().from_orm(offerer)


class GetOfferersListResponseModel(BaseModel):
    offerers: list[GetOfferersResponseModel]
    nbTotalResults: int


class GetOffererListQueryModel(BaseModel):
    keywords: str | None
    page: int | None = 1
    paginate: int | None = 10


class ReimbursementPointResponseModel(BaseModel):
    venueId: int
    venueName: str
    iban: str


class ReimbursementPointListResponseModel(BaseModel):
    __root__: list[ReimbursementPointResponseModel]
