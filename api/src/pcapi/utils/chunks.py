import inspect
from itertools import islice
import typing


T = typing.TypeVar("T")


def get_chunks(input_data: typing.Iterable[T], chunk_size: int) -> typing.Generator[list[T], None, None]:
    """
    Build chunks of `chunk_size` max from an iterable.
    eg. get_chuks([1, 2, 3], 2) -> ([1, 2], [2])
    """
    if not inspect.isgenerator(input_data):
        # if `input_data` is not a generator, the while loop will not
        # consume anything and always get the same first items from
        # `input_data`
        input_data = (elt for elt in input_data)

    while True:
        chunk = list(islice(input_data, chunk_size))
        if chunk:
            yield chunk

        if len(chunk) < chunk_size:
            break
