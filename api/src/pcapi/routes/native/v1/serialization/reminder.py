from pcapi.routes.serialization import ConfiguredBaseModel


class PostReminderRequest(ConfiguredBaseModel):
    offer_id: int


class ReminderOfferResponse(ConfiguredBaseModel):
    id: int


class ReminderResponse(ConfiguredBaseModel):
    id: int
    offer: ReminderOfferResponse


class GetRemindersResponse(ConfiguredBaseModel):
    reminders: list[ReminderResponse]
