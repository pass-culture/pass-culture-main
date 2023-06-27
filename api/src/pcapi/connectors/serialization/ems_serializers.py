from decimal import Decimal

from pcapi.routes.serialization import BaseModel


class Session(BaseModel):
    id: str
    date: str
    features: list[str]
    pass_culture_price: Decimal


class Event(BaseModel):
    id: str
    allocine_id: int
    title: str
    director: str | None
    synopsis: str | None
    bill_url: str | None
    duration: int
    sessions: list[Session]


class Site(BaseModel):
    id: str
    name: str
    address: str
    zip_code: str
    city: str
    events: list[Event]


class CinemasProgramsResponse(BaseModel):
    sites: list[Site]
    version: int
