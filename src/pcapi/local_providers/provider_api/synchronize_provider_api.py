from datetime import datetime
import logging
import time
from typing import Counter
from typing import Generator

from sqlalchemy.sql.sqltypes import DateTime

from pcapi.core.providers.api import synchronize_stocks
from pcapi.core.providers.models import VenueProvider
from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def synchronize_venue_provider(venue_provider: VenueProvider) -> None:
    venue = venue_provider.venue
    provider = venue_provider.provider
    start_sync_date = datetime.utcnow()

    start = time.perf_counter()
    logger.info("Starting synchronization of venue=%s provider=%s", venue.id, provider.name)
    provider_api = provider.getProviderAPI()

    stats = Counter()
    for raw_stocks in _get_stocks_by_batch(
        venue_provider.venueIdAtOfferProvider, provider_api, venue_provider.lastSyncDate
    ):
        stock_details = _build_stock_details_from_raw_stocks(raw_stocks, venue_provider.venueIdAtOfferProvider)
        operations = synchronize_stocks(stock_details, venue, provider_id=provider.id)
        stats += Counter(operations)

    venue_provider.lastSyncDate = start_sync_date
    repository.save(venue_provider)
    logger.info(
        "Ended synchronization of venue=%s provider=%s",
        venue.id,
        provider.name,
        extra={
            "venue": venue.id,
            "provider": provider.name,
            "duration": time.perf_counter() - start,
            **stats,
        },
    )


def _get_stocks_by_batch(siret: str, provider_api: ProviderAPI, modified_since: DateTime) -> Generator:
    last_processed_provider_reference = ""

    while True:
        response = provider_api.validated_stocks(
            siret=siret,
            last_processed_reference=last_processed_provider_reference,
            modified_since=modified_since.strftime("%Y-%m-%dT%H:%M:%SZ") if modified_since else "",
        )
        raw_stocks = response.get("stocks", [])

        if not raw_stocks:
            break

        yield raw_stocks

        last_processed_provider_reference = raw_stocks[-1]["ref"]


def _build_stock_details_from_raw_stocks(raw_stocks: list[dict], venue_siret: str) -> list[dict]:
    stock_details = {}
    for stock in raw_stocks:
        stock_details[stock["ref"]] = {
            "products_provider_reference": stock["ref"],
            "offers_provider_reference": stock["ref"] + "@" + venue_siret,
            "stocks_provider_reference": stock["ref"] + "@" + venue_siret,
            "available_quantity": stock["available"],
        }

    return list(stock_details.values())
