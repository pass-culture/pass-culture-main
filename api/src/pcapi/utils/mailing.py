import logging
from datetime import datetime

from pcapi import settings
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offers.models import Stock
from pcapi.utils.date import utc_datetime_to_department_timezone


logger = logging.getLogger(__name__)


def build_pc_pro_reset_password_link(token_value: str) -> str:
    return f"{settings.PRO_URL}/mot-de-passe-perdu?token={token_value}"


def get_event_datetime(stock: CollectiveStock | Stock) -> datetime:
    start_value = stock.startDatetime if isinstance(stock, CollectiveStock) else stock.beginningDatetime

    if not start_value:
        raise ValueError("Event stock is missing a beginningDatetime")

    if isinstance(stock, Stock):
        departement_code = stock.offer.venue.departementCode
        if stock.offer.offererAddress is not None:
            departement_code = stock.offer.offererAddress.address.departmentCode
        elif stock.offer.venue.offererAddress is not None:
            departement_code = stock.offer.venue.offererAddress.address.departmentCode
    else:
        departement_code = stock.collectiveOffer.venue.departementCode

    if not departement_code:
        return start_value

    return utc_datetime_to_department_timezone(start_value, departement_code)
