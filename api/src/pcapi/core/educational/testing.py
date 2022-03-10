from typing import Union

from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse


adage_requests: list[dict[str, Union[EducationalBookingResponse, str]]] = []


def reset_requests() -> None:
    global adage_requests  # pylint: disable=global-statement
    adage_requests = []
