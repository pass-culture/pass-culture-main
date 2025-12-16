from pcapi.routes.serialization import HttpBodyModel


class OfferImageV2(HttpBodyModel):
    url: str
    credit: str | None = None


class HeadLineOfferResponseModel(HttpBodyModel):
    id: int
    name: str
    image: OfferImageV2 | None = None
    venue_id: int


class HeadlineOfferCreationBodyModel(HttpBodyModel):
    offer_id: int


class HeadlineOfferDeleteBodyModel(HttpBodyModel):
    offerer_id: int
