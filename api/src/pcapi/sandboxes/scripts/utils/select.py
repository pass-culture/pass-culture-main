from typing import Iterable
from typing import TypeVar


T = TypeVar("T")


def remove_every(elements: Iterable[T], remove_modulo: int) -> list[T]:
    # we keep (remove_modulo - 1) / remove_modulo of len(elements)
    return [element for (index, element) in enumerate(elements) if index % remove_modulo]
