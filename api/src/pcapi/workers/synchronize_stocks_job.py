import logging

from pcapi.core.offerers.repository import find_venue_by_id
from pcapi.core.providers import api
from pcapi.core.providers import constants
from pcapi.core.providers.models import StockDetail
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.workers import worker
from pcapi.workers.decorators import job


logger = logging.getLogger(__name__)


@job(worker.low_queue)
def synchronize_stocks_job(serialized_stock_details: list[dict], venue_id: int) -> None:
    pc_provider = get_provider_by_local_class(constants.PASS_CULTURE_STOCKS_FAKE_CLASS_NAME)

    stock_details = [
        StockDetail(
            products_provider_reference=stock_detail["products_provider_reference"],
            offers_provider_reference=stock_detail["offers_provider_reference"],
            stocks_provider_reference=stock_detail["stocks_provider_reference"],
            venue_reference=stock_detail["stocks_provider_reference"],
            available_quantity=stock_detail["available_quantity"],
            price=stock_detail["price"],
        )
        for stock_detail in serialized_stock_details
    ]

    venue = find_venue_by_id(venue_id)
    if not venue:  # unlikely, since `venue_id` comes from us
        raise ValueError(f"Could not find venue {venue_id}")
    operations = api.synchronize_stocks(stock_details, venue, provider_id=pc_provider.id)
    logger.info(
        "Processed stocks synchronization",
        extra={
            "venue": venue_id,
            "stocks": len(stock_details),
            **operations,
        },
    )
