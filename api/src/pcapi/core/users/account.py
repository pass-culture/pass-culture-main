from pcapi.routes.serialization import ConfiguredBaseModel


class NotificationSubscriptions(ConfiguredBaseModel):
    marketing_email: bool
    marketing_push: bool
    subscribed_themes: list[str] = []


class TrustedDevice(ConfiguredBaseModel):
    device_id: str
    os: str | None
    source: str | None

    class Config:
        anystr_strip_whitespace = True
