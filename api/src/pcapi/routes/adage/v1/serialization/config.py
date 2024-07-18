from datetime import datetime

from pcapi.routes.serialization import BaseModel
from pcapi.utils.date import format_into_utc_date
from pydantic import ConfigDict


class AdageBaseResponseModel(BaseModel):
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={datetime: format_into_utc_date})
