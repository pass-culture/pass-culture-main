search_store: dict[str, dict[int, dict]] = {}


def reset_search_store() -> None:
    global search_store  # pylint: disable=global-statement  # noqa: PLW0603 (global-statement)
    search_store = {"offers": {}, "venues": {}, "collective-offers-templates": {}, "collective-offers": {}}


reset_search_store()
