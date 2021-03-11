from pcapi.serialization.utils import to_camel

from . import BaseModel


class BookOfferRequest(BaseModel):
    stock_id: str
    quantity: int

    class Config:
        alias_generator = to_camel
