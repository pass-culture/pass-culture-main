from pcapi.routes.serialization import ConfiguredBaseModel


class PostReminderRequest(ConfiguredBaseModel):
    offer_id: int
