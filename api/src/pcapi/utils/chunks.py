import inspect
from itertools import islice
import typing


T = typing.TypeVar("T")
Chunks = typing.Generator[list[T], None, None]
BaseGenerator = typing.Generator[T, None, None]
IterableOrGenerator = typing.Union[typing.Iterable[T], BaseGenerator]


def get_chunks(chunk_size: int, src: IterableOrGenerator) -> Chunks:
    """
    Build a generator that yields `chunk_size` sized chunks from an
    iterable.
    """
    if not inspect.isgenerator(src):
        src = _list_to_generator(src)

    while True:
        chunk = list(islice(src, chunk_size))
        if chunk:
            yield chunk

        if len(chunk) < chunk_size:
            break


def _list_to_generator(src: typing.Iterable[T]) -> BaseGenerator:
    for item in src:
        yield item
