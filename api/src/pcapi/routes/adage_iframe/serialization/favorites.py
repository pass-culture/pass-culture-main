from datetime import datetime

from pcapi.routes.adage_iframe.serialization import offers as serialize_offers
from pcapi.routes.serialization import BaseModel
from pcapi.utils.date import format_into_utc_date


class FavoritesResponseModel(BaseModel):
    favoritesTemplate: list[serialize_offers.CollectiveOfferTemplateResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}
