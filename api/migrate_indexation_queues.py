# fmt: off
from pcapi.flask_app import app; app.app_context().push()
# fmt: on


QUEUES = (
    ("search:algolia:offer-ids:list", "search:algolia:offer-ids:set"),
    ("search:algolia:offer-ids-in-error:list", "search:algolia:offer-ids-in-error:set"),
    ("search:algolia:venue-ids-for-offers:list", "search:algolia:venue-ids-for-offers:set"),
    ("search:algolia:venue-ids-to-index:list", "search:algolia:venue-ids-to-index:set"),
    ("search:algolia:venue-ids-in-error-to-index:list", "search:algolia:venue-ids-in-error-to-index:set"),
    (
        "search:algolia:collective-offer-template-ids-to-index:list",
        "search:algolia:collective-offer-template-ids-to-index:set",
    ),
    (
        "search:algolia:collective-offer-template-ids-in-error-to-index:list",
        "search:algolia:collective-offer-template-ids-in-error-to-index:set",
    ),
)

redis = app.redis_client

for origin_queue, target_queue in QUEUES:
    ids = redis.lrange(origin_queue, 0, -1)
    if not ids:
        continue
    redis.sadd(target_queue, *ids)
    redis.delete(origin_queue)
    print(f"Moved {len(ids)} ids from {origin_queue} to {target_queue}")

print("Done.")
