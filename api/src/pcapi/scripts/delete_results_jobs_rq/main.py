import logging

from redis import Redis

from pcapi.flask_app import app


logger = logging.getLogger(__name__)


def clear_results_without_ttl(redis_cli: Redis) -> None:
    cursor = 0
    keys_deleted = 0
    while True:
        cursor, keys = redis_cli.scan(cursor, match="rq:results:*", count=100)
        for key in keys:
            ttl = redis_cli.ttl(key)
            if ttl > 500:
                redis_cli.delete(key)
                keys_deleted += 1
        if cursor == 0:
            logger.info("Clé supprimées : %s", keys_deleted)
            break


if __name__ == "__main__":
    with app.app_context():
        clear_results_without_ttl(app.redis_client)
