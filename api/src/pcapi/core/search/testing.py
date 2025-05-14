import typing


search_store: dict[str, dict[typing.Union[int, str], dict]] = {}


def reset_search_store() -> None:
    global search_store  # noqa: PLW0603 (global-statement)
    search_store = {
        "artists": {},
        "offers": {},
        "venues": {},
        "collective-offers-templates": {},
        "collective-offers": {},
    }


reset_search_store()
