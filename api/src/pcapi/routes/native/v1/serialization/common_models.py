from pcapi.routes.serialization import HttpBodyModel


class DeviceInfo(HttpBodyModel):
    """
    This serializer has 3 unused fields: font_scale, resolution and screen_zoom_level
    They are not used by the backend and accepted here just to fit with what's the front is sending.
    In future API version we might need to remove them.
    """

    device_id: str
    os: str | None = None
    source: str | None = None
    # TODO remove the following fields in future api version
    font_scale: float | None = None
    resolution: str | None = None
    screen_zoom_level: float | None = None
