from pcapi.routes.serialization import HttpBodyModel


class PostReminderRequest(HttpBodyModel):
    offer_id: int


class ReminderOfferResponse(HttpBodyModel):
    id: int


class ReminderResponse(HttpBodyModel):
    id: int
    offer: ReminderOfferResponse


class GetRemindersResponse(HttpBodyModel):
    reminders: list[ReminderResponse]
