search_store = None


def reset_search_store():
    global search_store  # pylint: disable=global-statement
    search_store = {"offers": {}, "venues": {}, "collective-offers-templates": {}, "collective-offers": {}}


reset_search_store()
