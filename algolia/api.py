import os
from typing import Dict, List

from algoliasearch.search_client import SearchClient
from algoliasearch.search_index import SearchIndex

ALGOLIA_APPLICATION_ID = os.environ.get('ALGOLIA_APPLICATION_ID')
ALGOLIA_API_KEY = os.environ.get('ALGOLIA_API_KEY')
ALGOLIA_INDEX_NAME = os.environ.get('ALGOLIA_INDEX_NAME')


def init_connection() -> SearchIndex:
    return SearchClient \
        .create(ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY) \
        .init_index(ALGOLIA_INDEX_NAME)


def add_objects(objects: List[Dict]) -> None:
    init_connection() \
        .save_objects(objects)


def add_object(object: Dict) -> None:
    init_connection() \
        .save_object(object)


def clean_algolia_index() -> None:
    init_connection() \
        .clear_objects()


def delete_objects(object_ids: List[str]) -> None:
    init_connection() \
        .delete_objects(object_ids)


def delete_object(object_id: str) -> None:
    init_connection() \
        .delete_object(object_id)
