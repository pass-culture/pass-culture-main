from datetime import datetime
from typing import Optional

import pcapi.core.bookings.api as bookings_api
from pcapi.core.categories import subcategories
from pcapi.domain.beneficiary_bookings.active_mediation import ActiveMediation
from pcapi.domain.beneficiary_bookings.thumb_url import ThumbUrl
from pcapi.utils.human_ids import humanize


# FIXME: This class reimplements (with minor variations) methods of
# the `Booking` model. We should get rid of it.
class BeneficiaryBooking:
    def __init__(  # pylint: disable=redefined-builtin
        self,
        amount: int,
        cancellationDate: Optional[datetime],
        dateCreated: datetime,
        dateUsed: Optional[datetime],
        id: int,
        isCancelled: bool,
        isUsed: bool,
        quantity: int,
        stockId: int,
        token: str,
        userId: int,
        offerId: int,
        name: str,
        subcategoryId: str,
        url: Optional[str],
        email: str,
        beginningDatetime: Optional[datetime],
        venueId: int,
        departementCode: str,
        description: str,
        durationMinutes: int,
        extraData: dict,
        isDuo: bool,
        withdrawalDetails: Optional[str],
        mediaUrls: list[str],
        isNational: bool,
        venueName: str,
        address: str,
        postalCode: str,
        city: str,
        latitude: float,
        longitude: float,
        price: float,
        productId: int,
        thumbCount: int,
        active_mediations: list[ActiveMediation],
        activationCode: Optional[str],
        displayAsEnded: Optional[bool],
    ):
        self.price = price
        self.longitude = longitude
        self.latitude = latitude
        self.city = city
        self.postalCode = postalCode
        self.address = address
        self.venueName = venueName
        self.isNational = isNational
        self.mediaUrls = mediaUrls
        self.withdrawalDetails = withdrawalDetails
        self.isDuo = isDuo
        self.extraData = extraData
        self.durationMinutes = durationMinutes
        self.description = description
        self.amount = amount
        self.cancellationDate = cancellationDate
        self.dateCreated = dateCreated
        self.dateUsed = dateUsed
        self.id = id
        self.isCancelled = isCancelled
        self.isUsed = isUsed
        self.quantity = quantity
        self.stockId = stockId
        self.token = token
        self.userId = userId
        self.offerId = offerId
        self.name = name
        self.subcategoryId = subcategoryId
        self.url = url
        self.email = email
        self.beginningDatetime = beginningDatetime
        self.venueId = venueId
        self.departementCode = departementCode
        self.thumb_url = self._compute_thumb_url(
            active_mediations=active_mediations, product_id=productId, product_thumb_count=thumbCount
        )
        self.activationCode = activationCode
        self.displayAsEnded = displayAsEnded

    @staticmethod
    def _compute_thumb_url(
        active_mediations: list[ActiveMediation], product_id: int, product_thumb_count: int
    ) -> Optional[str]:
        if len(active_mediations) > 0:
            newest_mediation_id = sorted(active_mediations, key=lambda mediation: mediation.date_created, reverse=True)[
                0
            ].identifier
            return ThumbUrl.for_mediation(identifier=newest_mediation_id).url()
        if product_thumb_count > 0:
            return ThumbUrl.for_product(identifier=product_id).url()
        return None

    @property
    def booking_access_url(self) -> Optional[str]:
        url = self.url
        if url is None:
            return None
        if not url.startswith("http"):
            url = "http://" + url
        return (
            url.replace("{token}", self.token)
            .replace("{offerId}", humanize(self.offerId))
            .replace("{email}", self.email)
        )

    @property
    def is_event_expired(self) -> bool:
        if not self.beginningDatetime:
            return False
        return self.beginningDatetime <= datetime.utcnow()

    @property
    def is_booked_offer_digital(self) -> bool:
        return self.url is not None and self.url != ""

    @property
    def is_booked_offer_event(self) -> bool:
        return self.subcategory.is_event

    @property
    def qr_code(self) -> Optional[str]:
        if not self.is_event_expired and not self.isCancelled:
            return bookings_api.generate_qr_code(booking_token=self.token)
        if not self.isUsed and not self.isCancelled:
            return bookings_api.generate_qr_code(booking_token=self.token)
        return None

    @property
    def subcategory(self) -> subcategories.Subcategory:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId '{self.subcategoryId}' for BeneficiaryBooking {self.id}")
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]
