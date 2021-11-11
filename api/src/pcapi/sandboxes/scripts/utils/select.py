def pick_every(elements, pick_modulo):
    # we keep len(elements) / modulo
    return list(elements)[::pick_modulo]


def remove_every(elements, remove_modulo):
    # we keep (remove_modulo - 1) / remove_modulo of len(elements)
    return [element for (index, element) in enumerate(elements) if index % remove_modulo]
