import argparse
import json

from pcapi.app import app


app.app_context().push()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    redis_client = app.redis_client

    for key in redis_client.keys("cache:api:addresse:search:*"):
        cached_data = json.loads(redis_client.get(key))  # type: ignore [arg-type]
        if cached_data["features"] == [] and len(cached_data) == 2:
            # Basically, if the cached_data looks like this:
            # {'type': 'FeatureCollection', 'features': []}
            # Something went wrong on BAN API side and this is an improperly cached response
            # Usually, while not finding an address
            # BAN API respond with something like this:
            # {'type': 'FeatureCollection', 'version': 'draft', 'features': [], 'attribution': 'BAN', 'licence': 'ETALAB-2.0', 'query': 'Pouroi faire', 'filters': {'postcode': '97351'}, 'limit': 1}
            if args.dry_run:
                print(key)
            else:
                redis_client.delete(key)
