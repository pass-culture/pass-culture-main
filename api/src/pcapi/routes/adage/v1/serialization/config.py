from datetime import datetime

from pcapi.routes.serialization import BaseModel
from pcapi.utils.date import format_into_utc_date


class AdageBaseResponseModel(BaseModel):
    class Config:
        json_encoders = {datetime: format_into_utc_date}
