from pcapi.routes.serialization import HttpBodyModel


class BookCollectiveOfferRequest(HttpBodyModel):
    stockId: int


class BookCollectiveOfferResponse(HttpBodyModel):
    bookingId: int
