import enum
from functools import partial
import typing


class AllocineStocksPriceRule(Exception):
    pass


def default_price(*args: typing.Any) -> bool:
    return True


class PriceRule(enum.Enum):
    default = partial(default_price)

    def __call__(self, *args: typing.Any) -> bool:
        return self.value(*args)
