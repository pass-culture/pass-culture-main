from pcapi.routes.serialization import ConfiguredBaseModel


class PostReminderRequest(ConfiguredBaseModel):
    offer_id: int


class ReminderOfferResponse(ConfiguredBaseModel):
    id: int


class PostReminderResponse(ConfiguredBaseModel):
    id: int
    offer: ReminderOfferResponse
