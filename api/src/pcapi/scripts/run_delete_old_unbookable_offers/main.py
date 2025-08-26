import pcapi.core.offers.api as offers_api
from pcapi.app import app


app.app_context().push()


if __name__ == "__main__":
    offers_api.delete_unbookable_unbooked_old_offers(
        min_id=None,
        max_id=None,
        query_batch_size=5_000,
        filter_batch_size=2_500,
        delete_batch_size=32,
    )
