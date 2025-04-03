from pcapi.routes.serialization import BaseModel


class CreateOrUpdateEANOffersRequest(BaseModel):
    serialized_products_stocks: dict
    venue_id: int
    provider_id: int
    address_id: int | None = None
    address_label: str | None = None
