from pydantic import BaseModel as BaseModelV2


class OffererPayload(BaseModelV2):
    offerer_id: int


class VenuePayload(BaseModelV2):
    venue_id: int
