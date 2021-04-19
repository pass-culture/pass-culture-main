from algoliasearch.search_client import SearchClient
from algoliasearch.search_index import SearchIndex

from pcapi import settings


def init_connection() -> SearchIndex:
    client = SearchClient.create(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY)
    return client.init_index(settings.ALGOLIA_INDEX_NAME)


def add_objects(objects: list[dict]) -> None:
    init_connection().save_objects(objects)


def delete_objects(object_ids: list[int]) -> None:
    init_connection().delete_objects(object_ids)


def clear_index() -> None:
    init_connection().clear_objects()
