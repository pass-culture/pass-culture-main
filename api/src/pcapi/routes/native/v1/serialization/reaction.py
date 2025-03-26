import datetime

from pcapi.routes.serialization import ConfiguredBaseModel


class AvailableReactionBooking(ConfiguredBaseModel):
    name: str
    offer_id: int
    subcategory_id: str
    image: str | None
    dateUsed: datetime.datetime | None


class GetAvailableReactionsResponse(ConfiguredBaseModel):
    number_of_reactable_bookings: int
    bookings: list[AvailableReactionBooking]
