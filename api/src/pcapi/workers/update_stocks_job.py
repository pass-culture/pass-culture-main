import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def batch_delete_filtered_stocks_job(filters: dict) -> None:
    stocks = offers_repository.get_filtered_stocks(
        offer_id=filters["offer_id"],
        date=filters["date"],
        time=filters["time"],
        price_category_id=filters["price_category_id"],
    )
    offers_api.batch_delete_stocks(stocks.all())
