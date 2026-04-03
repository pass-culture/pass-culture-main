from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.routes.serialization import HttpBodyModel


class OfferCoordinatesResponse(HttpBodyModel):
    latitude: float | None = None
    longitude: float | None = None


class OfferImageResponse(HttpBodyModel):
    url: str
    credit: str | None = None


class BookOfferRequest(HttpBodyModel):
    stock_id: int
    quantity: int


class BookingDisplayStatusRequest(HttpBodyModel):
    ended: bool


class BookOfferResponse(HttpBodyModel):
    booking_id: int


class BookingVenueResponse(HttpBodyModel):
    id: int
    name: str
    public_name: str
    timezone: str
    banner_url: str | None = None
    is_open_to_public: bool

    @classmethod
    def build(cls, venue: Venue) -> "BookingVenueResponse":
        return cls(
            id=venue.id,
            name=venue.publicName,
            public_name=venue.publicName,
            timezone=venue.offererAddress.address.timezone,
            banner_url=venue.bannerUrl,
            is_open_to_public=venue.isOpenToPublic,
        )


class BookingOfferExtraData(HttpBodyModel):
    ean: str | None = None


class BookingOfferResponseAddress(HttpBodyModel):
    street: str | None = None
    postal_code: str
    city: str
    label: str | None = None
    coordinates: OfferCoordinatesResponse
    timezone: str


class BookingOfferResponse(HttpBodyModel):
    id: int
    address: BookingOfferResponseAddress | None = None
    booking_contact: str | None = None
    name: str
    extra_data: BookingOfferExtraData | None = None
    image: OfferImageResponse | None = None
    is_digital: bool
    is_permanent: bool
    subcategory_id: SubcategoryIdEnum
    url: str | None = None
    venue: BookingVenueResponse
    withdrawal_details: str | None = None
    withdrawal_type: WithdrawalTypeEnum | None = None
    withdrawal_delay: int | None = None

    @classmethod
    def build(cls, offer: Offer) -> "BookingOfferResponse":
        address_response = None
        offerer_address = offer.offererAddress or offer.venue.offererAddress

        if offerer_address:
            addr = offerer_address.address
            address_response = BookingOfferResponseAddress(
                street=addr.street,
                postal_code=addr.postalCode,
                city=addr.city,
                label=offerer_address.label,
                coordinates=OfferCoordinatesResponse(latitude=addr.latitude, longitude=addr.longitude),
                timezone=addr.timezone,
            )

        extra_data = None
        if offer.extraData and offer.extraData.get("ean"):
            extra_data = BookingOfferExtraData(ean=offer.extraData.get("ean"))

        return cls(
            id=offer.id,
            address=address_response,
            booking_contact=offer.bookingContact,
            name=offer.name,
            extra_data=extra_data,
            image=offer.image,
            is_digital=offer.isDigital,
            is_permanent=offer.isPermanent,
            subcategory_id=offer.subcategoryId,
            url=offer.url,
            venue=BookingVenueResponse.build(offer.venue),
            withdrawal_details=offer.withdrawalDetails,
            withdrawal_type=offer.withdrawalType,
            withdrawal_delay=offer.withdrawalDelay,
        )
