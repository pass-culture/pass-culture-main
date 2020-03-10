import os
from typing import Dict, List

from algoliasearch.search_client import SearchClient
from algoliasearch.search_index import SearchIndex

ALGOLIA_API_KEY = os.environ.get('ALGOLIA_API_KEY')
ALGOLIA_APPLICATION_ID = os.environ.get('ALGOLIA_APPLICATION_ID')
ALGOLIA_INDEX_NAME = os.environ.get('ALGOLIA_INDEX_NAME')


def init_connection() -> SearchIndex:
    return SearchClient \
        .create(ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY) \
        .init_index(ALGOLIA_INDEX_NAME)


def add_objects(objects: List[Dict]) -> None:
    init_connection() \
        .save_objects(objects)


def delete_objects(object_ids: List[str]) -> None:
    init_connection() \
        .delete_objects(object_ids)


def clear_index() -> None:
    init_connection() \
        .clear_objects()
