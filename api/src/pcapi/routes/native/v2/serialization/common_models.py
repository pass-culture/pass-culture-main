from pcapi.routes.serialization import HttpBodyModel


class DeviceInfoV2(HttpBodyModel):
    device_id: str
    os: str | None = None
    source: str | None = None
