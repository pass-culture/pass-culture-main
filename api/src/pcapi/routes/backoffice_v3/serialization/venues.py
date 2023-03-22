import datetime

from pcapi.routes.serialization import BaseModel

from .offerers import OffersStats


class LastOfferSyncStats(BaseModel):
    date: datetime.datetime | None
    provider: str | None


class VenueOffersStats(OffersStats):
    lastSync: LastOfferSyncStats


class VenueStats(BaseModel):
    stats: VenueOffersStats
    total_revenue: float


class VenueDmsStats(BaseModel):
    status: str
    subscriptionDate: datetime.datetime
    lastChangeDate: datetime.datetime
    url: str
