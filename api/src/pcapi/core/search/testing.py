import typing

from pcapi import settings


search_store: dict[str, dict[typing.Union[int, str], dict]] = {}


def reset_search_store() -> None:
    global search_store  # noqa: PLW0603 (global-statement)
    assert settings.ALGOLIA_ARTISTS_INDEX_NAME
    assert settings.ALGOLIA_OFFERS_INDEX_NAME
    assert settings.ALGOLIA_VENUES_INDEX_NAME
    assert settings.ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME
    search_store = {
        settings.ALGOLIA_ARTISTS_INDEX_NAME: {},
        settings.ALGOLIA_OFFERS_INDEX_NAME: {},
        settings.ALGOLIA_VENUES_INDEX_NAME: {},
        settings.ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME: {},
    }


reset_search_store()
