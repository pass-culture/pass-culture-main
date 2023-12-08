# fmt: off
from pcapi.flask_app import app; app.app_context().push()
# fmt: on


QUEUES = (
    ("search:algolia:offer_ids", "search:algolia:offer-ids:list"),
    ("search:algolia:offer_ids_in_error", "search:algolia:offer-ids-in-error:list"),
    ("search:algolia:venue_ids_for_offers", "search:algolia:venue-ids-for-offers:list"),
    ("search:algolia:venue-ids-to-index", "search:algolia:venue-ids-to-index:list"),
    ("search:algolia:venue-ids-in-error-to-index", "search:algolia:venue-ids-in-error-to-index:list"),
    ("search:algolia:collective-offer-ids-to-index", "search:algolia:collective-offer-ids-to-index:list"),
    (
        "search:algolia:collective-offer-template-ids-to-index",
        "search:algolia:collective-offer-template-ids-to-index:list",
    ),
    (
        "search:algolia:collective-offer-ids-in-error-to-index",
        "search:algolia:collective-offer-ids-in-error-to-index:list",
    ),
    (
        "search:algolia:collective-offer-template-ids-in-error-to-index",
        "search:algolia:collective-offer-template-ids-in-error-to-index:list",
    ),
)

redis = app.redis_client

for origin_queue, target_queue in QUEUES:
    ids = redis.smembers(origin_queue)
    if not ids:
        continue
    redis.lpush(target_queue, *ids)
    redis.delete(origin_queue)
    print(f"Moved {len(ids)} ids from {origin_queue} to {target_queue}")

print("Done.")
